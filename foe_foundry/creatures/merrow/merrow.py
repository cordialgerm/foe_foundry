from foe_foundry.statblocks import BaseStatblock

from ...ac_templates import NaturalArmor
from ...attack_template import AttackTemplate, natural, spell, weapon
from ...creature_types import CreatureType
from ...damage import DamageType
from ...movement import Movement
from ...powers import (
    PowerSelection,
)
from ...role_types import MonsterRole
from ...size import Size
from ...skills import Skills, Stats, StatScaling
from .._template import (
    GenerationSettings,
    Monster,
    MonsterTemplate,
    MonsterVariant,
)
from ..base_stats import base_stats
from . import powers

MerrowVariant = MonsterVariant(
    name="Merrow",
    description="Merrows are aquatic monstrosities that dwell in the depths of the sea. They are known for their brute strength and cunning tactics.",
    monsters=[Monster(name="Merrow", cr=2, srd_creatures=["Merrow"])],
)
MerrowBloodBlessed = MonsterVariant(
    name="Merrow Blood-Blessed",
    description="Merrow Blood-Blessed are powerful merrows that have been granted additional strength and resilience through dark rituals.",
    monsters=[
        Monster(name="Merrow Blood-Blessed", cr=4),
    ],
)
MerrowStormblessed = MonsterVariant(
    name="Merrow Storm-Blessed",
    description="Merrow Storm-Blessed are elite merrows that command the power of storms, using lightning and thunder to devastate their foes.",
    monsters=[
        Monster(name="Merrow Storm-Blessed", cr=8),
    ],
)
MerrowAbyssalLord = MonsterVariant(
    name="Merrow Abyssal Lord",
    description="Merrow Abyssal Lords are the most powerful of their kind, ruling over vast underwater territories with an iron fist.",
    monsters=[
        Monster(name="Merrow Abyssal Lord", cr=12, is_legendary=True),
    ],
)


class _MerrowTemplate(MonsterTemplate):
    def choose_powers(self, settings: GenerationSettings) -> PowerSelection:
        if settings.variant is MerrowVariant:
            return PowerSelection(loadouts=powers.MerrowLoadout)
        elif settings.variant is MerrowBloodBlessed:
            return PowerSelection(loadouts=powers.MerrowBloodBlessedLoadout)
        elif settings.variant is MerrowStormblessed:
            return PowerSelection(loadouts=powers.MerrowStormblessedLoadout)
        elif settings.variant is MerrowAbyssalLord:
            return PowerSelection(loadouts=powers.MerrowAbyssalLordLoadout)
        else:
            raise ValueError(f"Variant '{settings.variant.key}' is not recognized")

    def generate_stats(
        self, settings: GenerationSettings
    ) -> tuple[BaseStatblock, list[AttackTemplate]]:
        if settings.variant is MerrowStormblessed:
            attributes = [
                Stats.STR.scaler(StatScaling.Default, mod=2),
                Stats.DEX.scaler(StatScaling.Medium, mod=2),
                Stats.INT.scaler(StatScaling.Default, mod=3),
                Stats.WIS.scaler(StatScaling.Primary),
                Stats.CHA.scaler(StatScaling.Medium, mod=1),
            ]
        elif settings.variant is MerrowAbyssalLord:
            attributes = [
                Stats.STR.scaler(StatScaling.Primary),
                Stats.DEX.scaler(StatScaling.Medium, mod=2),
                Stats.INT.scaler(StatScaling.Default),
                Stats.WIS.scaler(StatScaling.Medium, mod=-1),
                Stats.CHA.scaler(StatScaling.Medium, mod=1),
            ]
        else:
            attributes = [
                Stats.STR.scaler(StatScaling.Primary),
                Stats.DEX.scaler(StatScaling.Medium, mod=2),
                Stats.INT.scaler(StatScaling.Default, mod=-2),
                Stats.WIS.scaler(StatScaling.Default),
                Stats.CHA.scaler(StatScaling.Medium, mod=-1),
            ]

        # STATS
        stats = base_stats(
            name=settings.creature_name,
            variant_key=settings.variant.key,
            template_key=settings.monster_template,
            monster_key=settings.monster_key,
            cr=settings.cr,
            stats=attributes,
            hp_multiplier=settings.hp_multiplier,
            damage_multiplier=settings.damage_multiplier,
        )

        stats = stats.copy(
            creature_type=CreatureType.Monstrosity,
            size=Size.Large,
            creature_class="Merrow",
            languages=["Abyssal", "Aquan"],
            senses=stats.senses.copy(darkvision=60),
        )

        # LEGENDARY
        if settings.is_legendary:
            stats = stats.as_legendary()

        # MOVEMENT
        stats = stats.copy(speed=Movement(walk=10, swim=40))

        # ARMOR CLASS
        stats = stats.add_ac_template(NaturalArmor).copy(uses_shield=False)

        # ATTACKS
        if settings.variant is MerrowStormblessed:
            attack = spell.Shock.with_display_name("Stormcaller's Strike")
            secondary_attack = None

            stats = stats.copy(
                secondary_damage_type=DamageType.Lightning,
            )

            # ROLES
            stats = stats.with_roles(
                primary_role=MonsterRole.Support,
            )

        else:
            attack = natural.Bite.with_display_name("Envenomed Maw")
            stats = stats.copy(
                secondary_damage_type=DamageType.Poison,
            )

            secondary_attack = weapon.JavelinAndShield.with_display_name(
                "Sharktooth Harpoon"
            ).copy(damage_scalar=0.9)

            # ROLES
            stats = stats.with_roles(
                primary_role=MonsterRole.Ambusher,
                additional_roles={
                    MonsterRole.Bruiser,
                },
            )

        # SKILLS
        stats = stats.grant_proficiency_or_expertise(Skills.Stealth)

        # SAVES
        if stats.cr >= 4:
            stats = stats.grant_save_proficiency(Stats.WIS)

        return stats, [attack, secondary_attack] if secondary_attack else [attack]


MerrowTemplate: MonsterTemplate = _MerrowTemplate(
    name="Merrow",
    tag_line="Aquatic Monstrosity",
    description="Merrows are aquatic monstrosities that dwell in the depths of the sea. They are known for their brute strength and cunning tactics.",
    treasure=[],
    variants=[
        MerrowVariant,
        MerrowBloodBlessed,
        MerrowStormblessed,
        MerrowAbyssalLord,
    ],
    species=[],
)

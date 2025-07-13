from foe_foundry.statblocks import BaseStatblock

from ...ac_templates import Unarmored, UnholyArmor
from ...attack_template import AttackTemplate, natural, spell
from ...creature_types import CreatureType
from ...damage import Condition, DamageType
from ...powers import (
    PowerSelection,
)
from ...role_types import MonsterRole
from ...skills import Stats, StatScaling
from ...spells import CasterType
from .._template import (
    GenerationSettings,
    Monster,
    MonsterTemplate,
    MonsterVariant,
)
from ..base_stats import base_stats
from . import powers

GhoulVariant = MonsterVariant(
    name="Ghoul",
    description="Ghouls rise from the bodies of cannibals and villains with depraved hungers. They form packs out of shared voracity.",
    monsters=[
        Monster(name="Ghoul", cr=1, srd_creatures=["Ghoul"]),
    ],
)

GhastVariant = MonsterVariant(
    name="Ghast",
    description="Ghasts are reeking, undying corpses closely related to ghouls. They hunger for the vices they enjoyed in life as much as they do for rotting flesh.",
    monsters=[
        Monster(name="Ghast", cr=2, srd_creatures=["Ghast"]),
    ],
)

GravelordVariant = MonsterVariant(
    name="Gravelord",
    description="Gravelords are ghouls that have been blessed by a dark power, granting them the ability to raise the dead.",
    monsters=[
        Monster(
            name="Ghast Gravelord", cr=6, other_creatures={"Ghast Dreadcaller": "mm25"}
        )
    ],
)


class _GhoulTemplate(MonsterTemplate):
    def choose_powers(self, settings: GenerationSettings) -> PowerSelection:
        if settings.monster_key == "ghoul":
            return PowerSelection(powers.LoadoutGhoul)
        elif settings.monster_key == "ghast":
            return PowerSelection(powers.LoadoutGhast)
        elif settings.monster_key == "ghast-gravelord":
            return PowerSelection(powers.LoadoutGhastGravelord)
        else:
            raise ValueError(f"Unknown ghoul variant: {settings.monster_key}")

    def generate_stats(
        self, settings: GenerationSettings
    ) -> tuple[BaseStatblock, list[AttackTemplate]]:
        name = settings.creature_name
        cr = settings.cr
        variant = settings.variant
        rng = settings.rng

        # STATS
        hp_multiplier = 0.825

        if variant is GravelordVariant:
            stats = [
                Stats.STR.scaler(StatScaling.Medium, mod=-1),
                Stats.DEX.scaler(StatScaling.Medium, mod=2),
                Stats.CON.scaler(StatScaling.Constitution, mod=-2),
                Stats.INT.scaler(StatScaling.Primary),
                Stats.WIS.scaler(StatScaling.Default, mod=-0.5),
                Stats.CHA.scaler(StatScaling.Medium),
            ]
        else:
            stats = [
                Stats.STR.scaler(StatScaling.Medium, mod=2),
                Stats.DEX.scaler(StatScaling.Primary),
                Stats.CON.scaler(StatScaling.Constitution, mod=-2),
                Stats.INT.scaler(StatScaling.Default, mod=-3),
                Stats.WIS.scaler(StatScaling.Default, mod=-0.5),
                Stats.CHA.scaler(StatScaling.Default, mod=-4),
            ]

        stats = base_stats(
            name=name,
            variant_key=settings.variant.key,
            template_key=settings.monster_template,
            monster_key=settings.monster_key,
            cr=cr,
            stats=stats,
            hp_multiplier=hp_multiplier * settings.hp_multiplier,
            damage_multiplier=settings.damage_multiplier,
        )

        stats = stats.copy(
            creature_type=CreatureType.Undead,
            languages=["Common"],
            creature_class="Ghoul",
            senses=stats.senses.copy(darkvision=60),
        )

        # ARMOR CLASS
        if variant is GravelordVariant:
            stats = stats.add_ac_template(UnholyArmor)
        else:
            stats = stats.add_ac_template(Unarmored)

        # ATTACKS
        attack = natural.Claw.with_display_name("Paralytic Claw")
        secondary_damage_type = DamageType.Poison

        if variant is GravelordVariant:
            secondary_attack = spell.Deathbolt.copy(
                damage_scalar=0.9
            ).with_display_name("Dread Bolt")
        else:
            secondary_attack = None

        stats = stats.copy(
            secondary_damage_type=secondary_damage_type,
        )

        ## SPELLCASTING
        if variant is GravelordVariant:
            stats = stats.grant_spellcasting(caster_type=CasterType.Arcane)

        # ROLES
        if variant is GravelordVariant:
            stats = stats.with_roles(
                primary_role=MonsterRole.Leader, additional_roles=MonsterRole.Skirmisher
            )
        else:
            stats = stats.with_roles(
                primary_role=MonsterRole.Bruiser,
                additional_roles=MonsterRole.Skirmisher,
            )

        # SAVES
        if stats.cr >= 2:
            stats = stats.grant_save_proficiency(Stats.WIS)

        # IMMUNITIES
        stats = stats.grant_resistance_or_immunity(
            immunities={DamageType.Poison},
            resistances={DamageType.Necrotic} if stats.cr >= 2 else set(),
            conditions={Condition.Poisoned, Condition.Charmed, Condition.Poisoned},
        )

        return stats, [attack, secondary_attack] if secondary_attack else [attack]


GhoulTemplate: MonsterTemplate = _GhoulTemplate(
    name="Ghoul",
    tag_line="Undead cannibals",
    description="Ghouls are horrid creatures that feast on the flesh of the living and the dead.",
    treasure=[],
    variants=[GhoulVariant, GhastVariant, GravelordVariant],
    species=[],
)

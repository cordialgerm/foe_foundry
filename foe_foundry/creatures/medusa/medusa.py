from foe_foundry.statblocks import BaseStatblock

from ...ac_templates import NaturalArmor
from ...attack_template import AttackTemplate, natural, weapon
from ...creature_types import CreatureType
from ...damage import DamageType
from ...powers import (
    PowerSelection,
    flags,
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

MedusaVariant = MonsterVariant(
    name="Medusa",
    description="Medusas are prideful creatures that inhabit sites of fallen glory. They have hair of living snakes and an infamous petrifying gaze.",
    monsters=[
        Monster(name="Medusa", cr=6, srd_creatures=["Medusa"]),
        Monster(name="Medusa Queen", cr=10, is_legendary=True),
    ],
)


class _MedusaTemplate(MonsterTemplate):
    def choose_powers(self, settings: GenerationSettings) -> PowerSelection:
        if settings.monster_key == "medusa":
            return PowerSelection(powers.LoadoutMedusa)
        elif settings.monster_key == "medusa-queen":
            return PowerSelection(powers.LoadoutMedusaQueen)
        else:
            raise ValueError(f"Unknown monster key: {settings.monster_key}")

    def generate_stats(
        self, settings: GenerationSettings
    ) -> tuple[BaseStatblock, list[AttackTemplate]]:
        name = settings.creature_name
        cr = settings.cr
        is_legendary = settings.is_legendary
        rng = settings.rng

        # STATS
        stats = base_stats(
            name=name,
            variant_key=settings.variant.key,
            template_key=settings.monster_template,
            monster_key=settings.monster_key,
            cr=cr,
            stats=[
                Stats.STR.scaler(StatScaling.Default, mod=-2),
                Stats.DEX.scaler(StatScaling.Primary),
                Stats.INT.scaler(StatScaling.Default),
                Stats.WIS.scaler(StatScaling.Default, mod=1),
                Stats.CHA.scaler(StatScaling.Medium, mod=2),
            ],
            hp_multiplier=settings.hp_multiplier,
            damage_multiplier=settings.damage_multiplier,
        )

        stats = stats.copy(
            creature_type=CreatureType.Monstrosity,
            size=Size.Medium,
            creature_class="Medusa",
            senses=stats.senses.copy(darkvision=150),
        )

        # LEGENDARY
        if is_legendary:
            stats = stats.as_legendary()

        # ARMOR CLASS
        stats = stats.add_ac_template(NaturalArmor)

        # ATTACKS
        attack = weapon.Longbow.with_display_name("Poisoned Arrows")
        stats = stats.copy(
            secondary_damage_type=DamageType.Poison,
        )

        secondary_attack = natural.Bite.with_display_name("Snake Hair")

        # ROLES
        stats = stats.with_roles(
            primary_role=MonsterRole.Skirmisher,
            additional_roles={
                MonsterRole.Ambusher,
                MonsterRole.Controller,
                MonsterRole.Artillery,
            },
        )

        # MOVEMENT
        stats = stats.with_flags(flags.NO_TELEPORT)

        # SKILLS
        stats = stats.grant_proficiency_or_expertise(
            Skills.Initiative, Skills.Deception, Skills.Perception, Skills.Stealth
        )

        # SAVES
        stats = stats.grant_save_proficiency(Stats.WIS)

        return stats, [attack, secondary_attack]


MedusaTemplate: MonsterTemplate = _MedusaTemplate(
    name="Medusa",
    tag_line="Snake-haired recluse with a petrifying gaze",
    description="Medusas are prideful creatures that inhabit sites of fallen glory. They have hair of living snakes and an infamous petrifying gaze.",
    environments=["Desert", "Dungeon"],
    treasure=[],
    variants=[MedusaVariant],
    species=[],
)

from foe_foundry.environs import Affinity, Biome, Development
from foe_foundry.statblocks import BaseStatblock

from ...ac_templates import NaturalArmor
from ...attack_template import AttackTemplate, natural
from ...creature_types import CreatureType
from ...damage import DamageType
from ...movement import Movement
from ...powers import PowerSelection
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

DireBunnyVariant = MonsterVariant(
    name="Dire Bunny",
    description="Dire bunnies are large, aggressive rabbits with sharp teeth and claws. They are often infected with a rabies-like disease that makes them more aggressive.",
    monsters=[
        Monster(name="Dire Bunny", cr=1),
        Monster(name="Dire Bunny Matriarch", cr=3),
    ],
)


class _DireBunnyTemplate(MonsterTemplate):
    def choose_powers(self, settings: GenerationSettings) -> PowerSelection:
        if settings.monster_key == "dire-bunny":
            return PowerSelection(powers.LoadoutDireBunny)
        elif settings.monster_key == "dire-bunny-matriarch":
            return PowerSelection(powers.LoadoutMatriarch)
        else:
            raise ValueError(
                f"Unexpected monster key {settings.monster_key} for Dire Bunny generation."
            )

    def generate_stats(
        self, settings: GenerationSettings
    ) -> tuple[BaseStatblock, list[AttackTemplate]]:
        name = settings.creature_name
        cr = settings.cr
        is_legendary = settings.is_legendary

        # STATS
        stats = [
            Stats.STR.scaler(StatScaling.Default),
            Stats.DEX.scaler(StatScaling.Primary, mod=2),
            Stats.CON.scaler(StatScaling.Constitution, mod=-2),
            Stats.INT.scaler(StatScaling.NoScaling, mod=-7),
            Stats.WIS.scaler(StatScaling.NoScaling, mod=2),
            Stats.CHA.scaler(StatScaling.NoScaling, mod=-4),
        ]

        stats = base_stats(
            name=name,
            variant_key=settings.variant.key,
            template_key=settings.monster_template,
            monster_key=settings.monster_key,
            cr=cr,
            stats=stats,
            hp_multiplier=0.8 * settings.hp_multiplier,
        )

        stats = stats.copy(
            creature_type=CreatureType.Monstrosity,
            size=Size.Large if cr >= 3 else Size.Medium,
            creature_class="Bunny",
            senses=stats.senses.copy(darkvision=60, blindsight=30),
        )

        # SPEED
        stats = stats.copy(speed=Movement(walk=50, burrow=25))

        # ARMOR CLASS
        stats = stats.add_ac_template(NaturalArmor)

        # ATTACKS
        attack = natural.Bite.with_display_name("Rabid Bite")
        stats = stats.copy(secondary_damage_type=DamageType.Poison)

        # ROLES
        stats = stats.with_roles(primary_role=MonsterRole.Skirmisher)

        # SAVES
        if is_legendary:
            stats = stats.grant_save_proficiency(Stats.WIS)

        # SKILLS
        stats = stats.grant_proficiency_or_expertise(
            Skills.Perception, Skills.Stealth, Skills.Initiative
        ).grant_proficiency_or_expertise(Skills.Initiative, Skills.Perception)

        return stats, [attack]


DireBunnyTemplate: MonsterTemplate = _DireBunnyTemplate(
    name="Dire Bunny",
    tag_line="Surprisingly vicious and quick.",
    description="Dire bunnies are large, aggressive rabbits with sharp teeth and claws. They are often infected with a rabies-like disease that makes them more aggressive.",
    treasure=[],
    variants=[DireBunnyVariant],
    species=[],
    environments=[
        (Biome.forest, Affinity.native),  # Natural rabbit habitat in woodlands
        (
            Biome.grassland,
            Affinity.native,
        ),  # Open meadows and prairies where rabbits thrive
        (
            Development.countryside,
            Affinity.common,
        ),  # May venture near farmlands and settlements
        (
            Biome.farmland,
            Affinity.common,
        ),  # Agricultural areas where rabbits naturally occur
        (
            Development.frontier,
            Affinity.uncommon,
        ),  # Edge settlements where wilderness meets civilization
    ],
)

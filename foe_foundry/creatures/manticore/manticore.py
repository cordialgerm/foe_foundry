from foe_foundry.environs import Affinity, Biome, Development, Terrain
from foe_foundry.statblocks import BaseStatblock

from ...ac_templates import NaturalArmor
from ...attack_template import AttackTemplate, natural
from ...creature_types import CreatureType
from ...movement import Movement
from ...powers import PowerSelection, flags
from ...role_types import MonsterRole
from ...size import Size
from ...skills import AbilityScore, Skills, StatScaling
from .._template import (
    GenerationSettings,
    Monster,
    MonsterTemplate,
    MonsterVariant,
)
from ..base_stats import base_stats
from . import powers

ManticoreVariant = MonsterVariant(
    name="Manticore",
    description="Manticores are bizarre amalgamations with the body of a lion, dragon-like wings, a bristling tail of barbed spines, and the leering face of a voracious human. They are known for their cruel appetites and even crueler wit.",
    monsters=[
        Monster(name="Manticore", cr=3, srd_creatures=["Manticore"]),
        Monster(name="Manticore Ravager", cr=6),
    ],
)


class _ManticoreTemplate(MonsterTemplate):
    def choose_powers(self, settings: GenerationSettings) -> PowerSelection:
        if settings.monster_key == "manticore":
            return PowerSelection(powers.LoadoutManticore)
        elif settings.monster_key == "manticore-ravager":
            return PowerSelection(powers.LoadoutManticoreRavager)
        else:
            raise ValueError(f"Unknown monster key: {settings.monster_key}")

    def generate_stats(
        self, settings: GenerationSettings
    ) -> tuple[BaseStatblock, list[AttackTemplate]]:
        name = settings.creature_name
        cr = settings.cr

        # STATS
        stats = base_stats(
            name=name,
            variant_key=settings.variant.key,
            template_key=settings.monster_template,
            monster_key=settings.monster_key,
            cr=cr,
            stats=[
                AbilityScore.STR.scaler(StatScaling.Primary),
                AbilityScore.DEX.scaler(StatScaling.Medium, mod=3),
                AbilityScore.CON.scaler(StatScaling.Constitution, mod=2),
                AbilityScore.INT.scaler(StatScaling.Default, mod=-5),
                AbilityScore.WIS.scaler(StatScaling.Medium, mod=-2),
                AbilityScore.CHA.scaler(StatScaling.Default, mod=-4),
            ],
            hp_multiplier=settings.hp_multiplier,
            damage_multiplier=settings.damage_multiplier,
        )

        stats = stats.copy(
            creature_type=CreatureType.Monstrosity,
            size=Size.Large,
            creature_class="Manticore",
            languages=["Common"],
            senses=stats.senses.copy(darkvision=60),
        )

        # ARMOR CLASS
        stats = stats.add_ac_template(NaturalArmor, ac_modifier=-1)

        # ATTACKS
        attack = natural.Claw.with_display_name("Cruel Claws")

        # ROLES
        stats = stats.with_roles(
            primary_role=MonsterRole.Artillery,
            additional_roles={
                MonsterRole.Skirmisher,
            },
        )

        # MOVEMENT
        stats = stats.with_flags(flags.NO_TELEPORT).copy(
            speed=Movement(walk=30, fly=50)
        )

        # SKILLS
        stats = stats.grant_proficiency_or_expertise(Skills.Intimidation)

        # SAVES
        if stats.cr >= 6:
            stats = stats.grant_save_proficiency(AbilityScore.WIS)

        return stats, [attack]


ManticoreTemplate: MonsterTemplate = _ManticoreTemplate(
    name="Manticore",
    tag_line="Flying hunters with spiked tails and sharper tongues",
    description="Manticores are bizarre amalgamations with the body of a lion, dragon-like wings, a bristling tail of barbed spines, and the leering face of a voracious human. They are known for their cruel appetites and even crueler wit.",
    treasure=[],
    variants=[ManticoreVariant],
    species=[],
    environments=[
        (Terrain.mountain, Affinity.native),  # Desolate cliffs and rocky peaks
        (
            Development.wilderness,
            Affinity.native,
        ),  # Harsh wilderness far from civilization
        (Development.ruin, Affinity.common),  # Ruined towers and abandoned structures
        (
            Terrain.hill,
            Affinity.common,
        ),  # Elevated hunting grounds with good visibility
        (Biome.desert, Affinity.uncommon),  # Arid wastelands they patrol
        (Development.frontier, Affinity.rare),  # Edge settlements they might raid
    ],
)

from foe_foundry.environs import Affinity, Biome, Development
from foe_foundry.statblocks import BaseStatblock

from ...ac_templates import Unarmored
from ...attack_template import AttackTemplate, natural
from ...creature_types import CreatureType
from ...damage import Condition, DamageType
from ...movement import Movement
from ...powers import PowerSelection
from ...role_types import MonsterRole
from ...senses import Senses
from ...size import Size
from ...skills import Stats, StatScaling
from .._template import (
    GenerationSettings,
    Monster,
    MonsterTemplate,
    MonsterVariant,
)
from ..base_stats import base_stats
from . import powers

GelatinousCubeVariant = MonsterVariant(
    name="Gelatinous Cube",
    description="A Gelatinous Cube is a silent, quivering mass of acidic goo that dissolves any organic material unfortunate enough to get caught inside. These cubes glide slowly and silently through dungeons, caverns, and other forgotten caverns, with eerie purpose, as if some deeper instinct compels their mindless patrol.",
    monsters=[
        Monster(name="Gelatinous Cube", cr=2, srd_creatures=["Gelatinous Cube"]),
        Monster(name="Ancient Gelatinous Cube", cr=6),
    ],
)


class _CubeTemplate(MonsterTemplate):
    def choose_powers(self, settings: GenerationSettings) -> PowerSelection:
        if settings.monster_key == "gelatinous-cube":
            return PowerSelection(powers.LoadoutGelatinousCube)
        elif settings.monster_key == "ancient-gelatinous-cube":
            return PowerSelection(powers.LoadoutAncientCube)
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
                Stats.STR.scaler(StatScaling.Primary, mod=-2),
                Stats.DEX.scaler(StatScaling.NoScaling, mod=-7),
                Stats.CON.scaler(StatScaling.Constitution, mod=6),
                Stats.INT.scaler(StatScaling.NoScaling, mod=-9),
                Stats.WIS.scaler(StatScaling.Medium, mod=-6),
                Stats.CHA.scaler(StatScaling.NoScaling, mod=-9),
            ],
            hp_multiplier=1.4 * settings.hp_multiplier,
            damage_multiplier=0.9 * settings.damage_multiplier,
        )

        stats = stats.copy(
            creature_type=CreatureType.Ooze,
            size=Size.Huge if cr >= 5 else Size.Large,
            creature_class="Gelatinous Cube",
            senses=Senses(blindsight=60),
            speed=Movement(walk=20, climb=20),
        )

        # ARMOR CLASS
        stats = stats.add_ac_template(Unarmored)

        # ATTACKS
        attack = natural.Slam.with_display_name("Pseudopod").copy(
            damage_type=DamageType.Acid
        )
        stats = stats.copy(
            secondary_damage_type=DamageType.Acid,
        )
        stats = stats.with_reduced_attacks(reduce_by=1)

        # ROLES
        stats = stats.with_roles(primary_role=MonsterRole.Ambusher)

        # IMMUNITIES
        stats = stats.grant_resistance_or_immunity(
            immunities={DamageType.Acid},
            conditions={
                Condition.Blinded,
                Condition.Charmed,
                Condition.Deafened,
                Condition.Exhaustion,
                Condition.Frightened,
                Condition.Prone,
            },
        )

        return stats, [attack]


GelatinousCubeTemplate: MonsterTemplate = _CubeTemplate(
    name="Gelatinous Cube",
    tag_line="Acidic, Nigh-Invisible Dungeon Cleaner",
    description="A Gelatinous Cube is a silent, quivering mass of acidic goo that dissolves any organic material unfortunate enough to get caught inside. These cubes glide slowly and silently through dungeons, caverns, and other forgotten caverns, with eerie purpose, as if some deeper instinct compels their mindless patrol.",
    treasure=[],
    environments=[
        (
            Biome.underground,
            Affinity.native,
        ),  # native to dungeons, caverns, and subterranean spaces
        (
            Development.ruin,
            Affinity.native,
        ),  # found in forgotten ruins and abandoned structures
        (
            Development.dungeon,
            Affinity.native,
        ),  # specifically designed for dungeon environments
        (
            Development.wilderness,
            Affinity.rare,
        ),  # occasionally found in natural cave systems
    ],
    variants=[GelatinousCubeVariant],
    species=[],
)

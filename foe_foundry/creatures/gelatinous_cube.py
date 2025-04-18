from ..ac_templates import Unarmored
from ..attack_template import natural
from ..creature_types import CreatureType
from ..damage import Condition, DamageType
from ..movement import Movement
from ..powers import (
    LOW_POWER,
    CustomPowerSelection,
    CustomPowerWeight,
    Power,
    select_powers,
)
from ..powers.creature import gelatinous_cube
from ..powers.creature_type import ooze
from ..powers.roles import ambusher
from ..role_types import MonsterRole
from ..senses import Senses
from ..size import Size
from ..skills import Stats, StatScaling
from ..statblocks import BaseStatblock
from .base_stats import base_stats
from .template import (
    CreatureTemplate,
    CreatureVariant,
    GenerationSettings,
    StatsBeingGenerated,
    SuggestedCr,
)

GelatinousCubeVariant = CreatureVariant(
    name="Gelatinous Cube",
    description="A Gelatinous Cube is a silent, quivering mass of acidic goo that dissolves any organic material unfortunate enough to get caught inside. These cubes glide slowly and silently through dungeons, caverns, and other forgotten caverns, with eeie purpose, as if some deeper instinct compels their mindless patrol.",
    suggested_crs=[
        SuggestedCr(name="Gelatinous Cube", cr=2, srd_creatures=["Gelatinous Cube"]),
        SuggestedCr(name="Ancient Gelatinous Cube", cr=6),
    ],
)


class _GelatinousCubeWeights(CustomPowerSelection):
    def __init__(self, stats: BaseStatblock, cr: float):
        self.stats = stats
        self.cr = cr

    def force_powers(self) -> list[Power]:
        powers = [gelatinous_cube.EngulfInOoze, ooze.Transparent]
        if self.cr >= 5:
            powers.append(ooze.SlimeSpray)
        return powers

    def power_delta(self) -> float:
        return LOW_POWER - 0.3 * sum(p.power_level for p in self.force_powers())

    def custom_weight(self, p: Power) -> CustomPowerWeight:
        powers = [
            gelatinous_cube.MetabolicSurge,
            gelatinous_cube.PerfectlyTransparent,
            ambusher.StealthySneak,
            ambusher.DeadlyAmbusher,
        ]

        if p in powers:
            # lower weight to smooth out power selection to be more even
            return CustomPowerWeight(0.1, ignore_usual_requirements=True)
        else:
            # don't select random powers as most won't fit the ooze very well
            return CustomPowerWeight(-1, ignore_usual_requirements=False)


def generate_gelatinous_cube(settings: GenerationSettings) -> StatsBeingGenerated:
    name = settings.creature_name
    cr = settings.cr
    rng = settings.rng
    # STATS
    stats = base_stats(
        name=name,
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
    stats = attack.alter_base_stats(stats)
    stats = attack.initialize_attack(stats)
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

    # POWERS
    features = []

    # ADDITIONAL POWERS
    stats, power_features, power_selection = select_powers(
        stats=stats,
        rng=rng,
        settings=settings.selection_settings,
        custom=_GelatinousCubeWeights(stats, cr),
    )
    features += power_features

    # FINALIZE
    stats = attack.finalize_attacks(stats, rng, repair_all=False)
    return StatsBeingGenerated(stats=stats, features=features, powers=power_selection)


GelatinousCubeTemplate: CreatureTemplate = CreatureTemplate(
    name="Gelatinous Cube",
    tag_line="Acidic, Nigh-Invisible Dungeon Cleaner",
    description="A Gelatinous Cube is a silent, quivering mass of acidic goo that dissolves any organic material unfortunate enough to get caught inside. These cubes glide slowly and silently through dungeons, caverns, and other forgotten caverns, with eeie purpose, as if some deeper instinct compels their mindless patrol.",
    environments=["Underdark"],
    treasure=[],
    variants=[GelatinousCubeVariant],
    species=[],
    callback=generate_gelatinous_cube,
)

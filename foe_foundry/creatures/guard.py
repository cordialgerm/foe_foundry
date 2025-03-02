import numpy as np

from ..ac_templates import ChainShirt, PlateArmor, SplintArmor
from ..attack_template import weapon
from ..creature_types import CreatureType
from ..powers import CustomPowerWeight, Power, select_powers
from ..powers.creature.guard import GuardPowers
from ..powers.legendary import make_legendary
from ..powers.themed.gadget import GrenadePowers, NetPowers
from ..powers.themed.organized import OrganizedPowers
from ..powers.themed.sneaky import SneakyPowers
from ..powers.themed.technique import TechniquePowers
from ..role_types import MonsterRole
from ..size import Size
from ..skills import Skills, Stats, StatScaling
from .base_stats import BaseStatblock, base_stats
from .species import AllSpecies
from .template import (
    CreatureSpecies,
    CreatureTemplate,
    CreatureVariant,
    StatsBeingGenerated,
    SuggestedCr,
)


class _CustomWeights:
    def __init__(self, stats: BaseStatblock, variant: CreatureVariant):
        self.stats = stats
        self.variant = variant

    def __call__(self, p: Power) -> CustomPowerWeight:
        if p in GuardPowers:
            return CustomPowerWeight(weight=2, ignore_usual_requirements=True)
        elif p in OrganizedPowers:
            return CustomPowerWeight(weight=1.25, ignore_usual_requirements=True)
        elif p in TechniquePowers:
            # we want to boost techniques, but we can't skip requirements for them
            return CustomPowerWeight(weight=1.5, ignore_usual_requirements=False)
        elif p in NetPowers or p in GrenadePowers:
            return CustomPowerWeight(weight=1.5, ignore_usual_requirements=True)
        elif p in SneakyPowers:
            # guards aren't usually sneaky, so downrank
            return CustomPowerWeight(weight=0.5, ignore_usual_requirements=False)
        else:
            return CustomPowerWeight(weight=1, ignore_usual_requirements=False)


GuardVariant = CreatureVariant(
    name="Guard",
    description="Guards are perceptive, but most have little martial training. They might be bouncers, lookouts, members of a city watch, or other keen-eyed warriors.",
    suggested_crs=[
        SuggestedCr(
            name="Watchman",
            cr=1 / 8,
            srd_creatures=["Guard"],
        ),
        SuggestedCr(name="Sergeant of the Watch", cr=1),
    ],
)
CommanderVariant = CreatureVariant(
    name="Captain of the Watch",
    description="Guard captains often have ample professional experience. They might be accomplished bodyguards, protectors of magic treasures, veteran watch members, or similar wardens.",
    suggested_crs=[
        SuggestedCr(
            name="Guard Captain",
            cr=4,
            other_creatures={"Guard Captain": "mm25"},
        ),
        SuggestedCr(name="Lord of the Watch", cr=8, is_legendary=True),
    ],
)


def generate_guard(
    name: str,
    cr: float,
    variant: CreatureVariant,
    species: CreatureSpecies,
    rng: np.random.Generator,
) -> StatsBeingGenerated:
    # STATS

    if variant is CommanderVariant:
        stat_scaling = [
            Stats.STR.scaler(StatScaling.Primary),
            Stats.DEX.scaler(StatScaling.Medium, mod=4),
            Stats.INT.scaler(StatScaling.Default),
            Stats.WIS.scaler(StatScaling.Medium, mod=2),
            Stats.CHA.scaler(StatScaling.Default, mod=1),
        ]
    else:
        stat_scaling = [
            Stats.STR.scaler(StatScaling.Primary),
            Stats.DEX.scaler(StatScaling.Medium),
            Stats.INT.scaler(StatScaling.Default),
            Stats.WIS.scaler(StatScaling.Medium, mod=1),
            Stats.CHA.scaler(StatScaling.Default),
        ]

    stats = base_stats(name=name, cr=cr, stats=stat_scaling)

    stats = stats.copy(
        creature_type=CreatureType.Humanoid,
        size=Size.Medium,
        languages=["Common"],
        creature_class="Guard",
    )

    # ARMOR CLASS
    if stats.cr >= 5:
        stats = stats.add_ac_template(PlateArmor)
    elif stats.cr >= 3:
        stats = stats.add_ac_template(SplintArmor)
    else:
        stats = stats.add_ac_template(ChainShirt)

    # ATTACKS
    attack = weapon.Crossbow
    secondary_attack = weapon.SpearAndShield

    stats = attack.alter_base_stats(stats, rng)
    stats = attack.initialize_attack(stats)
    stats = stats.copy(primary_damage_type=attack.damage_type)
    stats = secondary_attack.add_as_secondary_attack(stats)
    stats = stats.copy(uses_shield=True)

    # ROLES
    if variant is CommanderVariant:
        primary_role = MonsterRole.Leader
        additional_roles = [
            MonsterRole.Defender,
            MonsterRole.Artillery,
            MonsterRole.Soldier,
        ]
    else:
        primary_role = MonsterRole.Defender
        additional_roles = [MonsterRole.Artillery, MonsterRole.Soldier]

    stats = stats.with_roles(
        primary_role=primary_role,
        additional_roles=additional_roles,
    )

    # SKILLS
    stats = stats.grant_proficiency_or_expertise(Skills.Perception)
    if cr >= 4:
        stats = stats.grant_proficiency_or_expertise(
            Skills.Initiative, Skills.Athletics
        )

    # SAVES
    if cr >= 4:
        stats = stats.grant_save_proficiency(Stats.STR)
    if cr >= 8:
        stats = stats.grant_save_proficiency(Stats.WIS, Stats.DEX, Stats.CON)

    # POWERS
    features = []

    # SPECIES CUSTOMIZATIONS
    stats = species.alter_base_stats(stats)

    # ADDITIONAL POWERS
    stats, power_features, power_selection = select_powers(
        stats=stats,
        rng=rng,
        power_level=stats.recommended_powers,
        custom_weights=_CustomWeights(stats, variant),
    )
    features += power_features

    # FINALIZE
    stats = attack.finalize_attacks(stats, rng)

    # LEGENDARY
    if variant is CommanderVariant and stats.cr >= 8:
        stats, features = make_legendary(stats, features, has_lair=False)

    return StatsBeingGenerated(stats=stats, features=features, powers=power_selection)


GuardTemplate: CreatureTemplate = CreatureTemplate(
    name="Guard",
    tag_line="Sentries and Watch Members",
    description="Guards protect people, places, and things, either for pay or from a sense of duty. They might perform their duties vigilantly or distractedly. Some raise alarms at the first sign of danger and defend their charges with their lives. Others flee outright if their compensation doesn't match the danger they face.",
    environments=["Any"],
    treasure=[],
    variants=[GuardVariant, CommanderVariant],
    species=AllSpecies,
    callback=generate_guard,
)

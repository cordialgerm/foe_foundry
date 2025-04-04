from ..ac_templates import ChainShirt, PlateArmor, SplintArmor
from ..attack_template import weapon
from ..creature_types import CreatureType
from ..powers import (
    CustomPowerSelection,
    CustomPowerWeight,
    Power,
    PowerType,
    select_powers,
)
from ..powers.creature.guard import GuardPowers
from ..powers.themed.gadget import GrenadePowers, NetPowers
from ..powers.themed.organized import OrganizedPowers
from ..powers.themed.sneaky import SneakyPowers
from ..powers.themed.technique import TechniquePowers
from ..role_types import MonsterRole
from ..size import Size
from ..skills import Skills, Stats, StatScaling
from .base_stats import BaseStatblock, base_stats
from .species import AllSpecies, HumanSpecies
from .template import (
    CreatureTemplate,
    CreatureVariant,
    GenerationSettings,
    StatsBeingGenerated,
    SuggestedCr,
)


class _CustomWeights(CustomPowerSelection):
    def __init__(self, stats: BaseStatblock, variant: CreatureVariant):
        self.stats = stats
        self.variant = variant

    def custom_weight(self, p: Power) -> CustomPowerWeight:
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
            return CustomPowerWeight(weight=0.25, ignore_usual_requirements=False)
        elif p.power_type == PowerType.Species:
            # boost species powers but still respect requirements
            return CustomPowerWeight(weight=1.5, ignore_usual_requirements=False)
        else:
            return CustomPowerWeight(weight=0.75, ignore_usual_requirements=False)


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
    settings: GenerationSettings,
) -> StatsBeingGenerated:
    name = settings.creature_name
    cr = settings.cr
    variant = settings.variant
    species = settings.species if settings.species else HumanSpecies
    rng = settings.rng
    is_legendary = settings.is_legendary

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

    stats = base_stats(
        name=name,
        cr=cr,
        stats=stat_scaling,
        hp_multiplier=settings.hp_multiplier,
        damage_multiplier=settings.damage_multiplier,
    )

    # LEGENDARY
    if is_legendary:
        stats = stats.as_legendary(actions=2, resistances=2)

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

    stats = attack.alter_base_stats(stats)
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
        settings=settings.selection_settings,
        custom=_CustomWeights(stats, variant),
    )
    features += power_features

    # FINALIZE
    stats = attack.finalize_attacks(stats, rng)

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

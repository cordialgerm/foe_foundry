from ..ac_templates import NaturalArmor
from ..attack_template import natural
from ..creature_types import CreatureType
from ..damage import DamageType
from ..movement import Movement
from ..powers import (
    LOW_POWER,
    MEDIUM_POWER,
    CustomPowerSelection,
    CustomPowerWeight,
    Power,
    select_powers,
)
from ..powers.creature import wolf
from ..powers.creature_type import beast
from ..powers.themed import bestial, breath, earthy, flying, icy, monstrous, warrior
from ..role_types import MonsterRole
from ..size import Size
from ..skills import Skills, Stats, StatScaling
from ..statblocks import BaseStatblock
from .base_stats import base_stats
from .template import (
    CreatureTemplate,
    CreatureVariant,
    GenerationSettings,
    StatsBeingGenerated,
    SuggestedCr,
)

WolfVariant = CreatureVariant(
    name="Wolf",
    description="Wolves are pack hunters that stalk their prey with cunning and ferocity.",
    suggested_crs=[
        SuggestedCr(name="Wolf", cr=1 / 8, srd_creatures=["Wolf"]),
        SuggestedCr(name="Dire Wolf", cr=1, srd_creatures=["Dire Wolf"]),
    ],
)
FrostwolfVariant = CreatureVariant(
    name="Winter Wolf",
    description="Winter wolves are large, intelligent wolves with white fur and a breath weapon that can freeze their foes.",
    suggested_crs=[
        SuggestedCr(name="Winter Wolf", cr=3, srd_creatures=["Winter Wolf"]),
        SuggestedCr(name="Fellwinter Packlord", cr=6, is_legendary=True),
    ],
)


class _WolfWeights(CustomPowerSelection):
    def __init__(self, stats: BaseStatblock, variant: CreatureVariant):
        self.stats = stats
        self.variant = variant

    def force_powers(self) -> list[Power]:
        if self.variant is FrostwolfVariant:
            return [warrior.PackTactics, wolf.SnappingJaws, breath.FlashFreezeBreath]
        elif self.stats.cr >= 1:
            return [warrior.PackTactics, wolf.SnappingJaws]
        else:
            return [warrior.PackTactics]

    def power_delta(self) -> float:
        n = len(self.force_powers())
        if self.stats.cr == 1:
            return LOW_POWER
        elif self.stats.cr <= 3:
            return LOW_POWER - n * MEDIUM_POWER * 0.2
        else:
            return LOW_POWER - n * MEDIUM_POWER * 0.3

    def custom_weight(self, p: Power) -> CustomPowerWeight:
        powers = [
            monstrous.Pounce,
            bestial.OpportuneBite,
            bestial.RetributiveStrike,
            beast.FeedingFrenzy,
            beast.ScentOfWeakness,
            beast.WildInstinct,
        ] + wolf.WolfPowers

        suppress = earthy.EarthyPowers + flying.FlyingPowers

        if self.variant is FrostwolfVariant:
            powers += [icy.Blizzard, icy.IcyTomb, icy.Hoarfrost, icy.Frostbite]

        if p in suppress:
            return CustomPowerWeight(-1, ignore_usual_requirements=False)
        elif p in powers:
            return CustomPowerWeight(2.0, ignore_usual_requirements=True)
        else:
            return CustomPowerWeight(0.25, ignore_usual_requirements=False)


def generate_wolf(settings: GenerationSettings) -> StatsBeingGenerated:
    name = settings.creature_name
    cr = settings.cr
    rng = settings.rng
    variant = settings.variant
    is_legendary = settings.is_legendary

    # STATS
    if cr < 1:
        stats = [
            Stats.STR.scaler(StatScaling.NoScaling, mod=4),
            Stats.DEX.scaler(StatScaling.NoScaling, mod=5),
            Stats.CON.scaler(StatScaling.NoScaling, mod=2),
            Stats.INT.scaler(StatScaling.NoScaling, mod=-7),
            Stats.WIS.scaler(StatScaling.NoScaling, mod=2),
            Stats.CHA.scaler(StatScaling.NoScaling, mod=-4),
        ]
    else:
        stats = [
            Stats.STR.scaler(StatScaling.Primary, mod=1),
            Stats.DEX.scaler(StatScaling.NoScaling, mod=5),
            Stats.CON.scaler(StatScaling.Constitution, mod=1),
            Stats.INT.scaler(StatScaling.Default, mod=-7),
            Stats.WIS.scaler(StatScaling.NoScaling, mod=2),
            Stats.CHA.scaler(StatScaling.Default, mod=-4),
        ]

    hp_multiplier = 1.3 if cr < 1 else 1.0
    stats = base_stats(
        name=name,
        cr=cr,
        stats=stats,
        hp_multiplier=hp_multiplier * settings.hp_multiplier,
    )

    stats = stats.copy(
        creature_type=CreatureType.Beast if cr <= 1 else CreatureType.Monstrosity,
        size=Size.Medium if cr < 1 else Size.Large,
        creature_class="Wolf",
        senses=stats.senses.copy(darkvision=60),
    )

    # LEGENDARY
    if is_legendary:
        stats = stats.as_legendary(actions=2, resistances=2)

    # SPEED
    stats = stats.copy(speed=Movement(walk=40 if stats.cr < 1 else 50))

    # ARMOR CLASS
    stats = stats.add_ac_template(NaturalArmor)

    # ATTACKS
    attack = natural.Bite.with_display_name("Snapping Jaws")
    stats = attack.alter_base_stats(stats)
    stats = attack.initialize_attack(stats)

    if variant is WolfVariant:
        stats = stats.copy(secondary_damage_type=DamageType.Cold)

    # ROLES
    stats = stats.with_roles(primary_role=MonsterRole.Bruiser)

    # IMMUNITIES
    if variant is FrostwolfVariant:
        stats = stats.grant_resistance_or_immunity(immunities={DamageType.Cold})

    # SAVES
    if is_legendary:
        stats = stats.grant_save_proficiency(Stats.WIS)

    # SKILLS
    stats = stats.grant_proficiency_or_expertise(Skills.Perception, Skills.Stealth)
    stats = stats.grant_proficiency_or_expertise(Skills.Perception)

    # ADDITIONAL POWERS

    # POWERS
    features = []

    # ADDITIONAL POWERS
    stats, power_features, power_selection = select_powers(
        stats=stats,
        rng=rng,
        settings=settings.selection_settings,
        custom=_WolfWeights(stats, variant),
    )
    features += power_features

    # FINALIZE
    stats = attack.finalize_attacks(stats, rng, repair_all=False)
    return StatsBeingGenerated(stats=stats, features=features, powers=power_selection)


WolfTemplate: CreatureTemplate = CreatureTemplate(
    name="Wolf",
    tag_line="Bestial Pack Hunters",
    description="Wolves are pack hunters that stalk their prey with cunning and ferocity.",
    environments=["Arctic", "Forest", "Mountain", "Hill"],
    treasure=[],
    variants=[WolfVariant, FrostwolfVariant],
    species=[],
    callback=generate_wolf,
)

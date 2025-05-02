import numpy as np

from ..ac_templates import NaturalArmor
from ..attack_template import natural
from ..creature_types import CreatureType
from ..damage import DamageType
from ..movement import Movement
from ..powers import (
    MEDIUM_POWER,
    CustomPowerSelection,
    CustomPowerWeight,
    Power,
    select_powers,
)
from ..powers.creature import dire_bunny
from ..powers.creature_type import beast
from ..powers.roles import soldier
from ..powers.themed import (
    aberrant,
    bestial,
    diseased,
    earthy,
    flying,
    illusory,
    monstrous,
    serpentine,
)
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

DireBunnyVariant = CreatureVariant(
    name="Dire Bunny",
    description="Dire bunnies are large, aggressive rabbits with sharp teeth and claws. They are often infected with a rabies-like disease that makes them more aggressive.",
    suggested_crs=[
        SuggestedCr(name="Dire Bunny", cr=1),
        SuggestedCr(name="Dire Bunny Matriarch", cr=3),
    ],
)


class _DireBunnyWeights(CustomPowerSelection):
    def __init__(
        self, stats: BaseStatblock, variant: CreatureVariant, rng: np.random.Generator
    ):
        self.stats = stats
        self.variant = variant
        self.rng = rng

        diseases = [diseased.FilthFever, diseased.BlindingSickness, diseased.Mindfire]
        disease_index = self.rng.choice(len(diseases))
        disease = diseases[disease_index]
        disease_power = next(
            p
            for p in diseased.RottenGraspPowers
            if p.disease == disease  # type: ignore
        )
        self.disease_power = disease_power

        leap_powers = [soldier.MightyLeap, monstrous.Pounce, dire_bunny.ThumpOfDread]
        leap_index = self.rng.choice(len(leap_powers))
        leap_power = leap_powers[leap_index]
        self.leap_power = leap_power

        self.hard_coded = diseased.RottenGraspPowers + leap_powers

    def force_powers(self) -> list[Power]:
        return [self.disease_power, self.leap_power]

    def power_delta(self) -> float:
        return MEDIUM_POWER - 0.25 * sum(p.power_level for p in self.force_powers())

    def custom_weight(self, p: Power) -> CustomPowerWeight:
        powers = [
            bestial.OpportuneBite,
            bestial.RetributiveStrike,
            beast.FeedingFrenzy,
            beast.ScentOfWeakness,
            beast.WildInstinct,
        ]

        suppress = (
            earthy.EarthyPowers
            + flying.FlyingPowers
            + aberrant.AberrantPowers
            + serpentine.SerpentinePowers
            + self.hard_coded  # already chose from similar powers
            + illusory.IllusoryPowers
        )

        if p in suppress:
            return CustomPowerWeight(-1, ignore_usual_requirements=False)
        elif p in dire_bunny.DireBunnyPowers:
            return CustomPowerWeight(2.0, ignore_usual_requirements=False)
        elif p in powers:
            return CustomPowerWeight(1.5, ignore_usual_requirements=True)
        else:
            return CustomPowerWeight(0.25, ignore_usual_requirements=False)


def generate_dire_bunny(settings: GenerationSettings) -> StatsBeingGenerated:
    name = settings.creature_name
    cr = settings.cr
    rng = settings.rng
    variant = settings.variant
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
        template_key=settings.creature_template,
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
    stats = attack.alter_base_stats(stats)
    stats = attack.initialize_attack(stats)
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

    # ADDITIONAL POWERS

    # POWERS
    features = []

    # ADDITIONAL POWERS
    stats, power_features, power_selection = select_powers(
        stats=stats,
        rng=rng,
        settings=settings.selection_settings,
        custom=_DireBunnyWeights(stats, variant, rng),
    )
    features += power_features

    # FINALIZE
    stats = attack.finalize_attacks(stats, rng, repair_all=False)
    return StatsBeingGenerated(stats=stats, features=features, powers=power_selection)


DireBunnyTemplate: CreatureTemplate = CreatureTemplate(
    name="Dire Bunny",
    tag_line="Surprisingly vicious and quick.",
    description="Dire bunnies are large, aggressive rabbits with sharp teeth and claws. They are often infected with a rabies-like disease that makes them more aggressive.",
    environments=["Arctic", "Forest", "Mountain", "Hill"],
    treasure=[],
    variants=[DireBunnyVariant],
    species=[],
    callback=generate_dire_bunny,
)

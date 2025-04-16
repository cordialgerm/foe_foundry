from ..ac_templates import NaturalArmor
from ..attack_template import natural
from ..creature_types import CreatureType
from ..movement import Movement
from ..powers import (
    CustomPowerSelection,
    CustomPowerWeight,
    Power,
    flags,
    select_powers,
)
from ..powers.creature import manticore
from ..powers.creature_type import beast
from ..powers.themed import bestial, clever, flying, monstrous
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

ManticoreVariant = CreatureVariant(
    name="Manticore",
    description="Medusas are prideful creatures that inhabit sites of fallen glory. They have hair of living snakes and an infamous petrifying gaze.",
    suggested_crs=[
        SuggestedCr(name="Manticore", cr=3, srd_creatures=["Manticore"]),
        SuggestedCr(name="Manticore Ravager", cr=6),
    ],
)


class _ManticoreWeights(CustomPowerSelection):
    def __init__(self, stats: BaseStatblock, cr: float):
        self.stats = stats
        self.cr = cr

        self.powers = [
            beast.FeedingFrenzy,
            beast.BestialRampage,
            beast.WildInstinct,
            flying.WingedRetreat,
            flying.WingedCharge,
            flying.Flyby,
            bestial.MarkTheMeal,
            clever.IdentifyWeaknes,
            monstrous.Frenzy,
            monstrous.LingeringWound,
            monstrous.Pounce,
        ]
        self.force = [manticore.SpikeVolley, manticore.CruelJeer]

    def force_powers(self) -> list[Power]:
        return self.force

    def power_delta(self) -> float:
        return -0.25 * sum(p.power_level for p in self.force)

    def custom_weight(self, p: Power) -> CustomPowerWeight:
        if p in self.powers:
            return CustomPowerWeight(1.0, ignore_usual_requirements=True)
        else:
            # monstrosity power selection is not very good - use the hard-coded ones
            return CustomPowerWeight(-1)


def generate_manticore(settings: GenerationSettings) -> StatsBeingGenerated:
    name = settings.creature_name
    cr = settings.cr
    rng = settings.rng

    # STATS
    stats = base_stats(
        name=name,
        cr=cr,
        stats=[
            Stats.STR.scaler(StatScaling.Primary),
            Stats.DEX.scaler(StatScaling.Medium, mod=3),
            Stats.CON.scaler(StatScaling.Constitution, mod=2),
            Stats.INT.scaler(StatScaling.Default, mod=-5),
            Stats.WIS.scaler(StatScaling.Medium, mod=-2),
            Stats.CHA.scaler(StatScaling.Default, mod=-4),
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
    stats = attack.alter_base_stats(stats)
    stats = attack.initialize_attack(stats)

    # ROLES
    stats = stats.with_roles(
        primary_role=MonsterRole.Artillery,
        additional_roles={
            MonsterRole.Skirmisher,
        },
    )

    # MOVEMENT
    stats = stats.with_flags(flags.NO_TELEPORT).copy(speed=Movement(walk=30, fly=50))

    # SKILLS
    stats = stats.grant_proficiency_or_expertise(Skills.Intimidation)

    # SAVES
    if stats.cr >= 6:
        stats = stats.grant_save_proficiency(Stats.WIS)

    # POWERS
    features = []

    # ADDITIONAL POWERS
    stats, power_features, power_selection = select_powers(
        stats=stats,
        rng=rng,
        settings=settings.selection_settings,
        custom=_ManticoreWeights(stats, cr),
    )
    features += power_features

    # FINALIZE
    stats = attack.finalize_attacks(stats, rng, repair_all=False)
    return StatsBeingGenerated(stats=stats, features=features, powers=power_selection)


ManticoreTemplate: CreatureTemplate = CreatureTemplate(
    name="Manticore",
    tag_line="Flying hunters with spiked tails and sharper tongues",
    description="Manticores are bizarre amalgamations with the body of a lion, dragon-like wings, a bristling tail of barbed spines, and the leering face of a voracious human. They are known for their cruel appetites and even crueler wit.",
    environments=["Arctic", "Coasta", "Grassland", "Hill", "Mountain"],
    treasure=[],
    variants=[ManticoreVariant],
    species=[],
    callback=generate_manticore,
)

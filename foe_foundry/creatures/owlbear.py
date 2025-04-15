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
from ..powers.roles import bruiser
from ..powers.themed import (
    bestial,
    cruel,
    diseased,
    fearsome,
    monstrous,
    reckless,
    technique,
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

OwlbearVariant = CreatureVariant(
    name="Owlbear",
    description="Medusas are prideful creatures that inhabit sites of fallen glory. They have hair of living snakes and an infamous petrifying gaze.",
    suggested_crs=[
        SuggestedCr(name="Owlbear Cub", cr=1 / 2),
        SuggestedCr(name="Owlbear", cr=3, srd_creatures=["Owlbear"]),
        SuggestedCr(
            name="Savage Owlbear", cr=7, other_creatures={"Primeval Owlbear": "mm24"}
        ),
    ],
)


class _OwlbearWeights(CustomPowerSelection):
    def __init__(self, stats: BaseStatblock):
        self.stats = stats

    def custom_weight(self, p: Power) -> CustomPowerWeight:
        suppress = diseased.DiseasedPowers

        powers = [
            bruiser.Rend,
            bruiser.CleavingBlows,
            bestial.OpportuneBite,
            bestial.RetributiveStrike,
            cruel.BloodiedFrenzy,
            cruel.BrutalCritical,
            fearsome.FearsomeRoar,
            monstrous.Pounce,
            monstrous.LingeringWound,
            monstrous.Rampage,
            monstrous.Frenzy,
            monstrous.TearApart,
            reckless.Charger,
            reckless.Overrun,
            reckless.BloodiedRage,
            technique.BleedingAttack,
            technique.ProneAttack,
            technique.PushingAttack,
            technique.GrazingAttack,
        ]

        if p in suppress:
            return CustomPowerWeight(-1, ignore_usual_requirements=True)
        elif p in powers:
            return CustomPowerWeight(2, ignore_usual_requirements=True)
        else:
            return CustomPowerWeight(0.1, ignore_usual_requirements=False)


def generate_owlbear(settings: GenerationSettings) -> StatsBeingGenerated:
    name = settings.creature_name
    cr = settings.cr
    rng = settings.rng

    hp_multiplier = 0.95
    damage_multiplier = 1.0 if cr >= 6 else 1.15

    # STATS
    stats = base_stats(
        name=name,
        cr=cr,
        stats=[
            Stats.STR.scaler(StatScaling.Primary, mod=4 if cr >= 6 else 2),
            Stats.DEX.scaler(StatScaling.Medium, mod=0.5),
            Stats.CON.scaler(StatScaling.Constitution, mod=4 if cr >= 6 else 2),
            Stats.INT.scaler(StatScaling.NoScaling, mod=-2 if cr >= 6 else -7),
            Stats.WIS.scaler(StatScaling.Medium, mod=2 if cr >= 6 else 0.5),
            Stats.CHA.scaler(StatScaling.Default, mod=-3),
        ],
        hp_multiplier=hp_multiplier * settings.hp_multiplier,
        damage_multiplier=damage_multiplier * settings.damage_multiplier,
    )

    stats = stats.copy(
        creature_type=CreatureType.Monstrosity,
        size=Size.Large,
        creature_class="Owlbear",
        senses=stats.senses.copy(darkvision=60),
    )

    # ARMOR CLASS
    stats = stats.add_ac_template(NaturalArmor, ac_modifier=0 if cr >= 6 else -1)

    # ATTACKS
    attack = natural.Claw.with_display_name("Vicious Rend")
    stats = attack.alter_base_stats(stats)
    stats = attack.initialize_attack(stats)

    # ROLES
    stats = stats.with_roles(primary_role=MonsterRole.Bruiser)

    # MOVEMENT
    stats = stats.with_flags(flags.NO_TELEPORT).copy(speed=Movement(walk=40, climb=40))

    # SKILLS
    stats = stats.grant_proficiency_or_expertise(
        Skills.Perception
    ).grant_proficiency_or_expertise(Skills.Perception)

    if cr >= 6:
        stats = stats.grant_proficiency_or_expertise(Skills.Initiative)

    # SAVES
    if cr >= 6:
        stats = stats.grant_save_proficiency(Stats.WIS, Stats.CON)

    # POWERS
    features = []

    # ADDITIONAL POWERS
    stats, power_features, power_selection = select_powers(
        stats=stats,
        rng=rng,
        settings=settings.selection_settings,
        custom=_OwlbearWeights(stats),
    )
    features += power_features

    # FINALIZE
    stats = attack.finalize_attacks(stats, rng, repair_all=False)

    return StatsBeingGenerated(stats=stats, features=features, powers=power_selection)


OwlbearTemplate: CreatureTemplate = CreatureTemplate(
    name="Owlbear",
    tag_line="Unnaturally Territorial Predators",
    description="An Owlbear is a fearsome hybrid creature, combining the powerful frame of a bear with the hooked beak, feathers, and piercing eyes of a giant owl.",
    environments=["Forest", "Hills"],
    treasure=[],
    variants=[OwlbearVariant],
    species=[],
    callback=generate_owlbear,
)

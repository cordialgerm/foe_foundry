import numpy as np

from ..ac_templates import NaturalPlating
from ..attack_template import natural
from ..creature_types import CreatureType
from ..damage import Condition
from ..powers import (
    MEDIUM_POWER,
    CustomPowerSelection,
    CustomPowerWeight,
    Power,
    select_powers,
)
from ..powers.creature import gorgon
from ..powers.creature_type import beast, construct
from ..powers.roles import bruiser, defender
from ..powers.themed import bestial, cruel, monstrous, reckless, technique
from ..role_types import MonsterRole
from ..size import Size
from ..skills import Skills, Stats, StatScaling
from ..statblocks import BaseStatblock, MonsterDials
from ._data import (
    GenerationSettings,
    Monster,
    MonsterTemplate,
    MonsterVariant,
    StatsBeingGenerated,
)
from .base_stats import base_stats

GorgonVariant = MonsterVariant(
    name="Gorgon",
    description="Gorgon are iron bulls that exhale a toxic petrifying breath",
    monsters=[
        Monster(name="Gorgon", cr=5, srd_creatures=["Gorgon"]),
    ],
)


class _GorgonWeights(CustomPowerSelection):
    def __init__(self, stats: BaseStatblock, rng: np.random.Generator):
        self.stats = stats
        self.rng = rng

        techniques = [technique.ProneAttack, technique.PushingAttack]
        i = rng.choice(len(techniques))
        self.technique = techniques[i]

    def force_powers(self) -> list[Power]:
        return gorgon.GorgonPowers + [
            beast.Gore,
            self.technique,
            construct.ImmutableForm,
        ]

    def custom_weight(self, p: Power) -> CustomPowerWeight:
        powers = [
            bestial.Trample,
            construct.ConstructedGuardian,
            construct.ExplosiveCore,
            construct.ProtectivePlating,
            construct.SpellStoring,
            bruiser.CleavingBlows,
            bruiser.StunningBlow,
            defender.SpellReflection,
            defender.ZoneOfControl,
            monstrous.Frenzy,
            monstrous.Rampage,
            cruel.BrutalCritical,
            reckless.Charger,
            reckless.RelentlessEndurance,
            reckless.Toss,
            reckless.WildCleave,
        ]

        if p in powers:
            return CustomPowerWeight(3, ignore_usual_requirements=True)
        else:
            return CustomPowerWeight(0.25, ignore_usual_requirements=False)


def generate_gorgon(settings: GenerationSettings) -> StatsBeingGenerated:
    name = settings.creature_name
    cr = settings.cr
    rng = settings.rng

    # STATS
    stats = base_stats(
        name=name,
        variant_key=settings.variant.key,
        template_key=settings.monster_template,
        monster_key=settings.monster_key,
        cr=cr,
        stats=[
            Stats.STR.scaler(StatScaling.Primary, mod=2),
            Stats.DEX.scaler(StatScaling.Default, mod=-1),
            Stats.CON.scaler(StatScaling.Constitution, mod=4),
            Stats.INT.scaler(StatScaling.Default, mod=-9),
            Stats.WIS.scaler(StatScaling.Default, mod=1),
            Stats.CHA.scaler(StatScaling.Default, mod=-5),
        ],
        hp_multiplier=1.2 * settings.hp_multiplier,
        damage_multiplier=0.95 * settings.damage_multiplier,
    )

    stats = stats.copy(
        creature_type=CreatureType.Construct,
        size=Size.Large,
        creature_class="Gorgon",
        senses=stats.senses.copy(darkvision=60),
    )

    # SPEED
    stats = stats.copy(speed=stats.speed.delta(10))

    # ARMOR CLASS
    stats = stats.add_ac_template(NaturalPlating, ac_modifier=2)

    # ATTACKS
    attack = natural.Stomp.with_display_name("Iron Hooves")
    stats = attack.alter_base_stats(stats)
    stats = attack.initialize_attack(stats)

    # ROLES
    stats = stats.with_roles(
        primary_role=MonsterRole.Bruiser,
        additional_roles={
            MonsterRole.Defender,
        },
    )

    # IMMUNITIES
    stats = stats.grant_resistance_or_immunity(
        conditions={Condition.Exhaustion, Condition.Petrified}
    )

    # SKILLS
    stats = stats.grant_proficiency_or_expertise(
        Skills.Perception
    ).grant_proficiency_or_expertise(Skills.Perception)  # expertise

    # ADDITIONAL POWERS

    stats = stats.apply_monster_dials(
        dials=MonsterDials(recommended_powers_modifier=MEDIUM_POWER)
    )

    # POWERS
    features = []

    # ADDITIONAL POWERS
    stats, power_features, power_selection = select_powers(
        stats=stats,
        rng=rng,
        settings=settings.selection_settings,
        custom=_GorgonWeights(stats, rng),
    )
    features += power_features

    # FINALIZE
    stats = attack.finalize_attacks(stats, rng, repair_all=False)
    return StatsBeingGenerated(stats=stats, features=features, powers=power_selection)


GorgonTemplate: MonsterTemplate = MonsterTemplate(
    name="Gorgon",
    tag_line="Bull-Like Constructs with Petrifying Breath",
    description="Gorgons are ferocious bull-like constructs with with iron plates and a toxic, petrifying breath",
    environments=["Forest", "Grassland", "Hill"],
    treasure=[],
    variants=[GorgonVariant],
    species=[],
    callback=generate_gorgon,
)

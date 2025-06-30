from ...ac_templates import NaturalPlating
from ...attack_template import natural
from ...creature_types import CreatureType
from ...damage import Condition
from ...powers import (
    MEDIUM_POWER,
    PowerSelection,
    select_powers,
)
from ...role_types import MonsterRole
from ...size import Size
from ...skills import Skills, Stats, StatScaling
from ...statblocks import MonsterDials
from .._data import (
    GenerationSettings,
    Monster,
    MonsterTemplate,
    MonsterVariant,
    StatsBeingGenerated,
)
from ..base_stats import base_stats
from . import powers

GorgonVariant = MonsterVariant(
    name="Gorgon",
    description="Gorgon are iron bulls that exhale a toxic petrifying breath",
    monsters=[
        Monster(name="Gorgon", cr=5, srd_creatures=["Gorgon"]),
    ],
)


def choose_powers(settings: GenerationSettings) -> PowerSelection:
    if settings.monster_key == "gorgon":
        return PowerSelection(powers.LoadoutGorgon)
    else:
        raise ValueError(f"Unknown monster key: {settings.monster_key}. ")


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

    # fewer, more powerful attacks
    stats = stats.with_set_attacks(2)

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
        custom=choose_powers(settings),
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

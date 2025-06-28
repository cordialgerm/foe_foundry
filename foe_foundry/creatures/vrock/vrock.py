from ...ac_templates import UnholyArmor
from ...attack_template import natural
from ...creature_types import CreatureType
from ...damage import Condition, DamageType
from ...movement import Movement
from ...powers import NewPowerSelection, select_powers
from ...role_types import MonsterRole
from ...size import Size
from ...skills import Stats, StatScaling
from .._data import (
    GenerationSettings,
    Monster,
    MonsterTemplate,
    MonsterVariant,
    StatsBeingGenerated,
)
from ..base_stats import base_stats
from . import powers

VrockVariant = MonsterVariant(
    name="Vrock",
    description="Vrocks are screeching vulture-like harbringers of chaos and destruction that carry disease and pestilance from the lower planes.",
    monsters=[
        Monster(name="Vrock", cr=6, srd_creatures=["Vrock"]),
    ],
)


def choose_powers(settings: GenerationSettings) -> NewPowerSelection:
    return NewPowerSelection(loadouts=powers.LoadoutVrock, rng=settings.rng)


def generate_vrock(settings: GenerationSettings) -> StatsBeingGenerated:
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
            Stats.STR.scaler(StatScaling.Primary),
            Stats.DEX.scaler(StatScaling.Medium, mod=2),
            Stats.CON.scaler(StatScaling.Constitution, mod=4),
            Stats.INT.scaler(StatScaling.Default, mod=-4),
            Stats.WIS.scaler(StatScaling.Default, mod=2),
            Stats.CHA.scaler(StatScaling.Default, mod=-4),
        ],
        hp_multiplier=1.2 * settings.hp_multiplier,
        damage_multiplier=settings.damage_multiplier,
    )

    stats = stats.copy(
        creature_type=CreatureType.Fiend,
        languages=["Abyssal; telepathy 120 ft."],
        creature_class="Vrock",
        creature_subtype="Demon",
        senses=stats.senses.copy(darkvision=120),
        size=Size.Large,
        speed=Movement(walk=40, fly=60),
    )

    # ARMOR CLASS
    stats = stats.add_ac_template(UnholyArmor)

    # ATTACKS
    attack = natural.Claw.with_display_name("Diseased Talons")
    stats = attack.alter_base_stats(stats)
    stats = attack.initialize_attack(stats)
    stats = stats.copy(
        secondary_damage_type=DamageType.Poison,
    )

    # Vrocks use two attacks
    stats = stats.with_set_attacks(2)

    # ROLES
    stats = stats.with_roles(
        primary_role=MonsterRole.Skirmisher,
        additional_roles=[MonsterRole.Controller],
    )

    # SAVES
    stats = stats.grant_save_proficiency(Stats.DEX, Stats.WIS, Stats.CHA)

    # IMMUNITIES
    stats = stats.grant_resistance_or_immunity(
        immunities={DamageType.Poison},
        resistances={DamageType.Cold, DamageType.Lightning, DamageType.Fire},
        conditions={Condition.Poisoned},
    )

    # POWERS
    features = []

    stats, power_features, power_selection = select_powers(
        stats=stats,
        rng=rng,
        settings=settings.selection_settings,
        custom=choose_powers(settings),
    )
    features += power_features

    # FINALIZE
    stats = attack.finalize_attacks(stats, rng)

    return StatsBeingGenerated(stats=stats, features=features, powers=power_selection)


VrockTemplate: MonsterTemplate = MonsterTemplate(
    name="Vrock",
    tag_line="Demon of Carnage and Ruin",
    description="Vrocks are screeching vulture-like harbringers of chaos and destruction that carry disease and pestilance from the lower planes.",
    environments=["Planar (Abyss)"],
    treasure=[],
    variants=[VrockVariant],
    species=[],
    callback=generate_vrock,
)

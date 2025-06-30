from ...ac_templates import Breastplate
from ...attack_template import weapon
from ...creature_types import CreatureType
from ...damage import Condition, DamageType
from ...powers import PowerSelection, select_powers
from ...role_types import MonsterRole
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

WightVariant = MonsterVariant(
    name="Wight",
    description="Wights are the dead and frozen corpses of wicked champions of bygone eras whose evil deeds persist into undeath.",
    monsters=[
        Monster(name="Wight", cr=3, srd_creatures=["Wight"]),
        Monster(name="Wight Fell Champion", cr=6),
        Monster(name="Wight Dread Lord", cr=9, is_legendary=True),
    ],
)


def choose_powers(settings: GenerationSettings) -> PowerSelection:
    if settings.monster_key == "wight":
        return PowerSelection(powers.LoadoutWight)
    elif settings.monster_key == "wight-fell-champion":
        return PowerSelection(powers.LoadoutChampion)
    elif settings.monster_key == "wight-dread-lord":
        return PowerSelection(powers.LoadoutLegendary)
    else:
        raise ValueError(f"Unknown monster key: {settings.monster_key}")


def generate_wight(settings: GenerationSettings) -> StatsBeingGenerated:
    name = settings.creature_name
    cr = settings.cr
    variant = settings.variant
    rng = settings.rng
    is_legendary = settings.is_legendary

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
            Stats.CON.scaler(StatScaling.Constitution, mod=2),
            Stats.INT.scaler(StatScaling.Default),
            Stats.WIS.scaler(StatScaling.Medium),
            Stats.CHA.scaler(StatScaling.Medium, mod=3),
        ],
        hp_multiplier=1.45 * settings.hp_multiplier,
        damage_multiplier=settings.damage_multiplier,
    )

    # LEGENDARY
    if is_legendary:
        stats = stats.as_legendary()

    stats = stats.copy(
        creature_type=CreatureType.Undead,
        languages=["Common"],
        creature_class="Wight",
        senses=stats.senses.copy(darkvision=60),
    )

    # ARMOR CLASS
    stats = stats.add_ac_template(Breastplate)

    # ATTACKS
    attack = weapon.SwordAndShield.with_display_name("Icicle Sword")
    secondary_damage_type = DamageType.Cold

    stats = attack.alter_base_stats(stats)
    stats = attack.initialize_attack(stats)
    stats = stats.copy(secondary_damage_type=secondary_damage_type, uses_shield=False)

    # ROLES
    stats = stats.with_roles(
        primary_role=MonsterRole.Soldier, additional_roles=MonsterRole.Leader
    )

    # SAVES
    if stats.cr >= 6:
        stats = stats.grant_save_proficiency(Stats.CON, Stats.WIS)

    # IMMUNITIES
    stats = stats.grant_resistance_or_immunity(
        resistances={DamageType.Necrotic},
        immunities={DamageType.Poison},
        conditions={Condition.Poisoned, Condition.Exhaustion},
        vulnerabilities={DamageType.Fire},
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
    stats = attack.finalize_attacks(stats, rng, repair_all=False)

    return StatsBeingGenerated(stats=stats, features=features, powers=power_selection)


WightTemplate: MonsterTemplate = MonsterTemplate(
    name="Wight",
    tag_line="Deathly cold malignant warriors of old",
    description="Wights are the dead and frozen corpses of wicked champions of bygone eras whose evil deeds persist into undeath.",
    environments=["Desert", "Planar (Shadowfell)", "Swamp", "Underadarl", "Urban"],
    treasure=[],
    variants=[WightVariant],
    species=[],
    callback=generate_wight,
)

from ...ac_templates import NaturalPlating
from ...attack_template import natural
from ...creature_types import CreatureType
from ...damage import DamageType
from ...powers import (
    NewPowerSelection,
    select_powers,
)
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

BasiliskVariant = MonsterVariant(
    name="Basilisk",
    description="Basilisks are large, reptilian creatures with the ability to turn flesh to stone with their gaze. They are often found in rocky areas and caves, where they use their petrifying gaze to protect their territory.",
    monsters=[
        Monster(name="Basilisk", cr=3, srd_creatures=["Basilisk"]),
        Monster(name="Basilisk Broodmother", cr=8),
    ],
)


def _choose_powers(
    settings: GenerationSettings,
) -> NewPowerSelection:
    if settings.monster_key == "basilisk":
        return NewPowerSelection(loadouts=powers.LoadoutBasilisk, rng=settings.rng)
    elif settings.monster_key == "basilisk-broodmother":
        return NewPowerSelection(
            loadouts=powers.LoadoutBasiliskBroodmother, rng=settings.rng
        )
    else:
        raise ValueError(f"Unknown basilisk variant: {settings.monster_key}")


def generate_basilisk(settings: GenerationSettings) -> StatsBeingGenerated:
    name = settings.creature_name
    cr = settings.cr
    variant = settings.variant
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
            Stats.DEX.scaler(StatScaling.Default, mod=-2),
            Stats.INT.scaler(StatScaling.Default, mod=-6),
            Stats.WIS.scaler(StatScaling.Medium, mod=-4),
            Stats.CHA.scaler(StatScaling.Default, mod=-3),
        ],
        hp_multiplier=settings.hp_multiplier,
        damage_multiplier=settings.damage_multiplier,
    )

    stats = stats.copy(
        creature_type=CreatureType.Monstrosity,
        size=Size.Medium,
        creature_class="Basilisk",
        senses=stats.senses.copy(darkvision=60),
    )

    # ARMOR CLASS
    stats = stats.add_ac_template(NaturalPlating)

    # ATTACKS
    attack = natural.Bite.with_display_name("Venomous Bite")
    stats = attack.alter_base_stats(stats)
    stats = attack.initialize_attack(stats)
    stats = stats.copy(
        secondary_damage_type=DamageType.Poison,
    )
    # ROLES
    stats = stats.with_roles(
        primary_role=MonsterRole.Bruiser, additional_roles=MonsterRole.Controller
    )

    # SAVES
    if cr >= 8:
        stats = stats.grant_save_proficiency(Stats.CON, Stats.STR, Stats.WIS)

    # POWERS
    features = []

    # ADDITIONAL POWERS
    stats, power_features, power_selection = select_powers(
        stats=stats,
        rng=rng,
        settings=settings.selection_settings,
        custom=_choose_powers(settings),
    )
    features += power_features

    # FINALIZE
    stats = attack.finalize_attacks(stats, rng, repair_all=False)
    return StatsBeingGenerated(stats=stats, features=features, powers=power_selection)


BasiliskTemplate: MonsterTemplate = MonsterTemplate(
    name="Basilisk",
    tag_line="Reptilian guardian with a petrifying gaze",
    description="Basilisks are large, reptilian creatures with the ability to turn flesh to stone with their gaze. They are often found in rocky areas and caves, where they use their petrifying gaze to protect their territory.",
    environments=["Mountain", "Underdark"],
    treasure=[],
    variants=[BasiliskVariant],
    species=[],
    callback=generate_basilisk,
)

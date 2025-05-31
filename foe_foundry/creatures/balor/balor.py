import numpy as np

from ...ac_templates import UnholyArmor
from ...attack_template import weapon
from ...creature_types import CreatureType
from ...damage import Condition, DamageType
from ...movement import Movement
from ...powers import NewPowerSelection, select_powers
from ...role_types import MonsterRole
from ...size import Size
from ...skills import Skills, Stats, StatScaling
from .._data import (
    GenerationSettings,
    Monster,
    MonsterTemplate,
    MonsterVariant,
    StatsBeingGenerated,
)
from ..base_stats import BaseStatblock, base_stats
from . import powers

BalorVariant = MonsterVariant(
    name="Balor",
    description="Balors embody demons' ruinous fury and hatred. Towering, winged terrors, these demonic warlords seethe with wrath, their rage erupting in waves of fire and as a pair of vicious weapons: a sword of crackling lightning and a whip of lashing flames.",
    monsters=[
        Monster(name="Balor", cr=19, srd_creatures=["Balor"]),
    ],
)

BalorGeneralVariant = MonsterVariant(
    name="Balor General",
    description="A balor general is a balor that has been granted the title of general by a demon lord. It is a powerful and respected leader among demons, commanding legions of lesser demons in the name of its master.",
    monsters=[
        Monster(name="Balor Dreadlord", cr=23, is_legendary=True),
    ],
)


def _custom_powers(
    stats: BaseStatblock, variant: MonsterVariant, rng: np.random.Generator
) -> NewPowerSelection:
    if variant is BalorVariant:
        return NewPowerSelection(powers.LoadoutBalor, rng=rng)
    elif variant is BalorGeneralVariant:
        return NewPowerSelection(powers.LoadoutBalorGeneral, rng=rng)
    else:
        raise ValueError(f"Unknown variant: {variant.name}")


def generate_balor(settings: GenerationSettings) -> StatsBeingGenerated:
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
            Stats.DEX.scaler(StatScaling.Medium, mod=1),
            Stats.INT.scaler(StatScaling.Medium, mod=4),
            Stats.WIS.scaler(StatScaling.Medium, mod=2),
            Stats.CHA.scaler(StatScaling.Medium, mod=6),
        ],
        hp_multiplier=settings.hp_multiplier,
        damage_multiplier=settings.damage_multiplier,
    )

    stats = stats.copy(
        creature_type=CreatureType.Fiend,
        languages=["Abyssal; telepathy 120 ft."],
        creature_class="Balor",
        creature_subtype="Demon",
        senses=stats.senses.copy(truesight=120),
        size=Size.Huge,
        speed=Movement(walk=40, fly=80),
    )

    # LEGENDARY
    if is_legendary:
        stats = stats.as_legendary()

    # ARMOR CLASS
    stats = stats.add_ac_template(UnholyArmor)

    # ATTACKS
    attack = weapon.Greatsword.with_display_name("Lightning Blade").copy(
        damage_type=DamageType.Lightning, split_secondary_damage=False
    )
    stats = attack.alter_base_stats(stats)
    stats = attack.initialize_attack(stats)
    stats = stats.copy(
        secondary_damage_type=DamageType.Fire,
    )

    ## ATTACK DAMAGE
    # zombies should have fewer attacks, but the attacks should hit hard!

    # lowering attacks on a legendary creature messes up formulas
    stats = stats.with_set_attacks(3)

    # ROLES
    stats = stats.with_roles(
        primary_role=MonsterRole.Bruiser,
        additional_roles=[MonsterRole.Soldier, MonsterRole.Leader],
    )

    # SAVES
    stats = stats.grant_save_proficiency(Stats.CON, Stats.WIS)

    # IMMUNITIES
    stats = stats.grant_resistance_or_immunity(
        immunities={DamageType.Fire, DamageType.Poison},
        resistances={DamageType.Cold, DamageType.Lightning},
        conditions={Condition.Poisoned, Condition.Frightened, Condition.Poisoned},
    )

    # SKILLS
    stats = stats.grant_proficiency_or_expertise(Skills.Perception, Skills.Initiative)
    stats = stats.grant_proficiency_or_expertise(Skills.Initiative)  # expertise

    # POWERS
    features = []

    stats, power_features, power_selection = select_powers(
        stats=stats,
        rng=rng,
        settings=settings.selection_settings,
        custom=_custom_powers(stats, variant, rng),
    )
    features += power_features

    # FINALIZE
    stats = attack.finalize_attacks(stats, rng)

    return StatsBeingGenerated(stats=stats, features=features, powers=power_selection)


BalorTemplate: MonsterTemplate = MonsterTemplate(
    name="Balor",
    tag_line="Demon of Overwhelming Rage",
    description="Balors embody demons' ruinous fury and hatred. Towering, winged terrors, these demonic warlords seethe with wrath, their rage erupting in waves of fire and as a pair of vicious weapons: a sword of crackling lightning and a whip of lashing flames. Demon lords and evil gods harness balors' rage by making balors commanders of armies or guardians of grave secrets.",
    environments=["Planar (Abyss)"],
    treasure=[],
    variants=[BalorVariant, BalorGeneralVariant],
    species=[],
    callback=generate_balor,
)

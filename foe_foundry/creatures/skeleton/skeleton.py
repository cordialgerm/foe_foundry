import numpy as np

from ...ac_templates import Breastplate, Unarmored
from ...attack_template import spell, weapon
from ...creature_types import CreatureType
from ...damage import Condition, DamageType
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
from ..base_stats import BaseStatblock, base_stats
from . import powers

SkeletonVariant = MonsterVariant(
    name="Skeleton",
    description="Skeletons are reanimated Humanoid bones bearing the equipment they had in life. They have rudimentary faculties and greater agility than zombies and similar shambling corpses. While they aren't capable of creating plans of their own, they avoid obvious barriers and self-destructive situations.",
    monsters=[
        Monster(name="Skeleton", cr=1 / 4, srd_creatures=["Skeleton"]),
    ],
)

GraveGuardVariant = MonsterVariant(
    name="Skeletal Grave Guard",
    description="Grave guards are skeletal warriors that have been reanimated with a greater degree of intelligence and purpose. They are often used as guardians for tombs or other sacred sites.",
    monsters=[
        Monster(name="Skeletal Grave Guard", cr=4),
    ],
)

BurningSkeletonVariant = MonsterVariant(
    name="Burning Skeleton",
    description="Flaming skeletons burn with unbridled necromantic energy. This magic grants them blazing attacks and greater awareness, which they use to command lesser Undead.",
    monsters=[
        Monster(
            name="Burning Skeleton", cr=3, other_creatures={"Flaming Skeleton": "mm25"}
        ),
        Monster(name="Burning Skeletal Champion", cr=6),
    ],
)

FreezingSkeletonVariant = MonsterVariant(
    name="Freezing Skeleton",
    description="Freezing skeletons are wreathed in the icy cold of the deathly river Styx.",
    monsters=[
        Monster(name="Freezing Skeleton", cr=3),
        Monster(name="Freezing Skeletal Champion", cr=6),
    ],
)


def _choose_powers(
    stats: BaseStatblock,
    variant: MonsterVariant,
    rng: np.random.Generator,
) -> NewPowerSelection:
    if variant is SkeletonVariant:
        return NewPowerSelection(loadouts=powers.LoadoutSkeleton, rng=rng)
    elif variant is GraveGuardVariant:
        return NewPowerSelection(loadouts=powers.LoadoutGraveGuard, rng=rng)
    elif variant is BurningSkeletonVariant:
        return NewPowerSelection(loadouts=powers.LoadoutBurningSkeleton, rng=rng)
    elif variant is FreezingSkeletonVariant:
        return NewPowerSelection(loadouts=powers.LoadoutFreezingSkeleton, rng=rng)
    else:
        raise ValueError(f"Unrecognized variant: {variant.name}")


def generate_skeleton(settings: GenerationSettings) -> StatsBeingGenerated:
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
            Stats.STR.scaler(StatScaling.Default),
            Stats.DEX.scaler(StatScaling.Primary),
            Stats.INT.scaler(StatScaling.Default, mod=-4),
            Stats.WIS.scaler(StatScaling.Default, mod=-2),
            Stats.CHA.scaler(StatScaling.Default, mod=-5),
        ],
        hp_multiplier=settings.hp_multiplier,
        damage_multiplier=settings.damage_multiplier,
    )

    stats = stats.copy(
        creature_type=CreatureType.Undead,
        size=Size.Medium,
        languages=["Common"],
        creature_class="Skeleton",
        senses=stats.senses.copy(darkvision=60),
    )

    # ARMOR CLASS
    if stats.cr >= 3:
        stats = stats.add_ac_template(Breastplate)
    else:
        stats = stats.add_ac_template(Unarmored)

    # ATTACKS
    if variant is SkeletonVariant:
        attack = weapon.Daggers.with_display_name("Bone Blades").copy(
            damage_scalar=0.75
        )  # dual wielding too scary at low CR
        secondary_damage_type = None
        secondary_attack = weapon.Shortbow.with_display_name("Bone Bow")
        n_attack = 1
    elif variant is GraveGuardVariant:
        attack = weapon.SpearAndShield.with_display_name("Bone Spear")
        secondary_damage_type = DamageType.Necrotic
        secondary_attack = weapon.Shortbow.with_display_name("Bone Bow").copy(
            damage_scalar=0.8
        )
        n_attack = 2
    elif variant is BurningSkeletonVariant:
        attack = weapon.Greatsword.with_display_name("Burning Blade")
        secondary_damage_type = DamageType.Fire
        secondary_attack = spell.Firebolt.with_display_name("Hurl Flames").copy(
            damage_scalar=0.8
        )
        n_attack = 2
    elif variant is FreezingSkeletonVariant:
        attack = weapon.Greatsword.with_display_name("Freezing Blade")
        secondary_damage_type = DamageType.Cold
        secondary_attack = spell.Frostbolt.with_display_name("Deathly Freeze").copy(
            damage_scalar=0.8
        )
        n_attack = 2

    stats = attack.alter_base_stats(stats)
    stats = attack.initialize_attack(stats)
    stats = stats.copy(
        secondary_damage_type=secondary_damage_type,
    )
    stats = stats.with_set_attacks(multiattack=n_attack)

    if secondary_attack is not None:
        stats = secondary_attack.add_as_secondary_attack(stats)

    # ROLES
    if variant is SkeletonVariant:
        primary_role = MonsterRole.Soldier
        additional_roles = []
    elif variant is GraveGuardVariant:
        primary_role = MonsterRole.Defender
        additional_roles = [MonsterRole.Leader]
    else:
        primary_role = MonsterRole.Soldier
        additional_roles = [MonsterRole.Leader] if cr >= 6 else []

    stats = stats.with_roles(
        primary_role=primary_role,
        additional_roles=additional_roles,
    )

    # SAVES
    if cr >= 3:
        stats = stats.grant_save_proficiency(Stats.CON)

    # IMMUNITIES
    stats = stats.grant_resistance_or_immunity(
        immunities={DamageType.Poison},
        conditions={Condition.Poisoned},
        vulnerabilities={DamageType.Bludgeoning},
    )
    if secondary_damage_type is not None:
        stats = stats.grant_resistance_or_immunity(immunities={secondary_damage_type})

    # POWERS
    features = []

    # ADDITIONAL POWERS
    stats, power_features, power_selection = select_powers(
        stats=stats,
        rng=rng,
        settings=settings.selection_settings,
        custom=_choose_powers(stats, variant, rng),
    )
    features += power_features

    # FINALIZE
    stats = attack.finalize_attacks(stats, rng, repair_all=False)
    if secondary_attack is not None:
        stats = secondary_attack.finalize_attacks(stats, rng, repair_all=False)
    return StatsBeingGenerated(stats=stats, features=features, powers=power_selection)


SkeletonTemplate: MonsterTemplate = MonsterTemplate(
    name="Skeleton",
    tag_line="Ossified Evil",
    description="Skeletons rise at the summons of necromancers and foul spirits. Whether they’re the remains of the ancient dead or fresh bones bound to morbid ambitions, they commit deathless work for whatever forces reanimated them, often serving as guardians, soldiers, or laborers.",
    environments=["Planar (Shadowfel)", "Underdark", "Urban"],
    treasure=[],
    variants=[
        SkeletonVariant,
        GraveGuardVariant,
        BurningSkeletonVariant,
        FreezingSkeletonVariant,
    ],
    species=[],
    callback=generate_skeleton,
)

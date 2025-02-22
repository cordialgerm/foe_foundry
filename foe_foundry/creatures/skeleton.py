import numpy as np

from ..ac_templates import MediumArmor, Unarmored, UnholyArmor
from ..attack_template import spell, weapon
from ..creature_types import CreatureType
from ..damage import Condition, DamageType
from ..powers import LOW_POWER, MEDIUM_POWER, Power, select_powers
from ..powers.creatures.undead import UndeadFortitude
from ..powers.themed.skeletal import SkeletalPowers
from ..role_types import MonsterRole
from ..size import Size
from ..skills import Stats, StatScaling
from ..statblocks import MonsterDials
from .base_stats import BaseStatblock, base_stats
from .template import (
    CreatureSpecies,
    CreatureTemplate,
    CreatureVariant,
    StatsBeingGenerated,
    SuggestedCr,
)

SkeletonVariant = CreatureVariant(
    name="Skeleton",
    description="Skeletons are reanimated Humanoid bones bearing the equipment they had in life. They have rudimentary faculties and greater agility than zombies and similar shambling corpses. While they aren't capable of creating plans of their own, they avoid obvious barriers and self-destructive situations.",
    suggested_crs=[
        SuggestedCr(name="Skeleton", cr=1 / 4, srd_creatures=["Skeleton"]),
        SuggestedCr(name="Skeletal Grave Guard", cr=4),
    ],
)

BurningSkeletonVariant = CreatureVariant(
    name="Burning Skeleton",
    description="Flaming skeletons burn with unbridled necromantic energy. This magic grants them blazing attacks and greater awareness, which they use to command lesser Undead.",
    suggested_crs=[
        SuggestedCr(
            name="Burning Skeleton", cr=3, other_creatures={"Flaming Skeleton": "mm25"}
        ),
        SuggestedCr(name="Burning Skeletal Champion", cr=6),
    ],
)

FreezingSkeletonVariant = CreatureVariant(
    name="Freezing Skeleton",
    description="Freezing skeletons are wreathed in the icy cold of the deathly river Styx.",
    suggested_crs=[
        SuggestedCr(name="Freezing Skeleton", cr=3),
        SuggestedCr(name="Freezing Skeletal Champion", cr=6),
    ],
)


class _CustomWeights:
    def __init__(self, stats: BaseStatblock, variant: CreatureVariant):
        self.stats = stats
        self.variant = variant

    def __call__(self, p: Power):
        powers = SkeletalPowers
        suppress_powers = [UndeadFortitude]
        if p in suppress_powers:
            return 0  # skeletons are not zombies
        elif p in powers:
            return 2
        else:
            return 1


def generate_skeleton(
    name: str,
    cr: float,
    variant: CreatureVariant,
    rng: np.random.Generator,
    species: CreatureSpecies | None = None,
) -> StatsBeingGenerated:
    # STATS
    stats = base_stats(
        name=name,
        cr=cr,
        stats=[
            Stats.STR.scaler(StatScaling.Default),
            Stats.DEX.scaler(StatScaling.Primary),
            Stats.INT.scaler(StatScaling.Default, mod=-4),
            Stats.WIS.scaler(StatScaling.Default, mod=-2),
            Stats.CHA.scaler(StatScaling.Default, mod=-5),
        ],
    )

    stats = stats.copy(
        creature_type=CreatureType.Undead,
        size=Size.Medium,
        languages=["Common"],
        creature_class="Skeleton",
        senses=stats.senses.copy(darkvision=60),
    )

    # ARMOR CLASS
    if variant is SkeletonVariant:
        if stats.cr >= 4:
            stats = stats.add_ac_template(MediumArmor)
        else:
            stats = stats.add_ac_template(Unarmored)
    else:
        stats = stats.add_ac_template(UnholyArmor)

    # ATTACKS
    if variant is SkeletonVariant:
        attack = weapon.SpearAndShield.with_display_name("Bone Spear")
        secondary_damage_type = DamageType.Necrotic if stats.cr >= 4 else None
        secondary_attack = weapon.Shortbow.with_display_name("Bone Bow")
    elif variant is BurningSkeletonVariant:
        attack = weapon.SwordAndShield.with_display_name("Burning Blade")
        secondary_damage_type = DamageType.Fire
        secondary_attack = spell.Firebolt.with_display_name("Hurl Flames")
    elif variant is FreezingSkeletonVariant:
        attack = weapon.SwordAndShield.with_display_name("Freezing Blade")
        secondary_damage_type = DamageType.Cold
        secondary_attack = spell.Frostbolt.with_display_name("Deathly Freeze")

    stats = attack.alter_base_stats(stats, rng)
    stats = attack.initialize_attack(stats)
    stats = stats.copy(
        secondary_damage_type=secondary_damage_type,
    )

    if secondary_attack is not None:
        stats = secondary_attack.add_as_secondary_attack(stats)

    # ROLES
    if variant is SkeletonVariant:
        primary_role = MonsterRole.Defender
        additional_roles = []
    else:
        primary_role = MonsterRole.Bruiser
        additional_roles = [MonsterRole.Artillery]

    stats = stats.with_roles(
        primary_role=primary_role,
        additional_roles=additional_roles,
    )

    # SAVES
    if cr >= 4:
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

    stats = stats.apply_monster_dials(
        MonsterDials(
            recommended_powers_modifier=LOW_POWER if stats.cr <= 2 else MEDIUM_POWER
        )
    )

    # ADDITIONAL POWERS
    stats, power_features, power_selection = select_powers(
        stats=stats,
        rng=rng,
        power_level=stats.recommended_powers,
        custom_weights=_CustomWeights(stats, variant),
    )
    features += power_features

    # FINALIZE
    stats = attack.finalize_attacks(stats, rng, repair_all=False)
    if secondary_attack is not None:
        stats = secondary_attack.finalize_attacks(stats, rng, repair_all=False)
    return StatsBeingGenerated(stats=stats, features=features, powers=power_selection)


SkeletonTemplate: CreatureTemplate = CreatureTemplate(
    name="Skeleton",
    tag_line="Ossified Evil",
    description="Skeletons rise at the summons of necromancers and foul spirits. Whether they’re the remains of the ancient dead or fresh bones bound to morbid ambitions, they commit deathless work for whatever forces reanimated them, often serving as guardians, soldiers, or laborers.",
    environments=["Planar (Shadowfel)", "Underdark", "Urban"],
    treasure=[],
    variants=[SkeletonVariant, BurningSkeletonVariant, FreezingSkeletonVariant],
    species=[],
    callback=generate_skeleton,
)

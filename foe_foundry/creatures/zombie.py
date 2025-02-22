import numpy as np

from ..ac_templates import Unarmored
from ..attack_template import natural
from ..creature_types import CreatureType
from ..damage import Condition, DamageType
from ..powers import Power, select_powers
from ..powers.creatures.undead import UndeadFortitude
from ..powers.legendary import make_legendary
from ..powers.themed.diseased import DiseasedPowers
from ..powers.themed.technique import GrapplingAttack
from ..powers.themed.zombie import ZombiePowers
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

ZombieVariant = CreatureVariant(
    name="Zombie",
    description="Humanoid zombies usually serve as guardians, servants, or soldiers for evil magic-users. In rare cases, foul magic might result in widespread reanimation of the dead, unleashing hordes of zombies to terrorize the living.",
    suggested_crs=[
        SuggestedCr(name="Zombie", cr=1 / 4, srd_creatures=["Zombie"]),
        SuggestedCr(name="Zombie Brute", cr=1),
        SuggestedCr(name="Zombie Gravewalker", cr=3),
    ],
)

ZombieOgreVariant = CreatureVariant(
    name="Zombie Ogre",
    description="Ogre zombies serve as tireless labor and undying weapons of war. These massive zombies possess the size and strength to break through barriers that repel smaller zombies.",
    suggested_crs=[
        SuggestedCr(name="Zombie Ogre", cr=2, srd_creatures=["Ogre Zombie"]),
        SuggestedCr(name="Zombie Giant", cr=8),
        SuggestedCr(name="Zombie Titan", cr=16, is_legendary=True),
    ],
)


class _CustomWeights:
    def __init__(self, stats: BaseStatblock, variant: CreatureVariant):
        self.stats = stats
        self.variant = variant

    def __call__(self, p: Power):
        if p in ZombiePowers:
            return 2.5
        elif p in DiseasedPowers:
            return 1.5
        else:
            return 0.5


def generate_zombie(
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
            Stats.STR.scaler(StatScaling.Primary),
            Stats.DEX.scaler(StatScaling.Default, mod=-4),
            Stats.CON.scaler(StatScaling.Constitution, mod=4),
            Stats.INT.scaler(StatScaling.Default, mod=-7),
            Stats.WIS.scaler(StatScaling.Default, mod=-4),
            Stats.CHA.scaler(StatScaling.Default, mod=-5),
        ],
    )

    stats = stats.copy(
        creature_type=CreatureType.Undead,
        languages=["Understands Common but can't speak"],
        creature_class="Zombie",
        senses=stats.senses.copy(darkvision=60),
    )

    # SIZE
    if variant is ZombieOgreVariant:
        size = Size.Huge if stats.cr >= 8 else Size.Large
    else:
        size = Size.Medium
    stats = stats.copy(size=size)

    # SPEED

    if variant is ZombieVariant:
        stats = stats.copy(speed=stats.speed.delta(-10))

    # Zombies don't use special movement so set this flag
    stats = stats.copy(has_unique_movement_manipulation=True)

    # ARMOR CLASS
    stats = stats.add_ac_template(Unarmored)

    # ATTACKS
    attack = natural.Slam.with_display_name(
        "Rotten Grasp"
    ).copy(
        split_secondary_damage=False  # zombies should be associated with poison but don't split damage to poison
    )
    secondary_damage_type = DamageType.Poison

    stats = attack.alter_base_stats(stats, rng)
    stats = attack.initialize_attack(stats)
    stats = stats.copy(
        secondary_damage_type=secondary_damage_type,
    )

    ## ATTACK DAMAGE
    # zombies should have fewer attacks, but the attacks should hit hard!
    stats = stats.with_reduced_attacks(reduce_by=1 if stats.cr <= 8 else 2)

    # ROLES
    stats = stats.with_roles(
        primary_role=MonsterRole.Bruiser,
    )

    # SAVES
    stats = stats.grant_save_proficiency(Stats.WIS)
    if stats.cr >= 4:
        stats = stats.grant_save_proficiency(Stats.CON)

    # IMMUNITIES
    stats = stats.grant_resistance_or_immunity(
        immunities={DamageType.Poison},
        conditions={Condition.Poisoned},
        vulnerabilities={DamageType.Radiant},
    )

    ## HP
    hp_multiplier = 1.3 if stats.cr <= 1 else 1.5
    stats = stats.apply_monster_dials(MonsterDials(hp_multiplier=hp_multiplier))

    # POWERS
    features = []

    # All zombies have Undead Fortitude and a Grappling Attack
    default_powers = [UndeadFortitude, GrapplingAttack]
    for feature in default_powers:
        stats = feature.modify_stats(stats)
        new_features = feature.generate_features(stats)
        features += new_features

    # subtract from the power budget
    power_tax = sum([p.power_level for p in default_powers]) / 8.0
    stats = stats.apply_monster_dials(
        MonsterDials(recommended_powers_modifier=-1 * power_tax)
    )

    # ADDITIONAL POWERS
    def custom_filter(power: Power) -> bool:
        return power not in default_powers

    stats, power_features, power_selection = select_powers(
        stats=stats,
        rng=rng,
        power_level=stats.recommended_powers,
        custom_filter=custom_filter,
        custom_weights=_CustomWeights(stats, variant),
    )
    features += power_features

    # FINALIZE
    stats = attack.finalize_attacks(stats, rng, repair_all=False)

    # LEGENDARY
    if variant is ZombieOgreVariant and stats.cr >= 16:
        stats, features = make_legendary(stats, features, has_lair=False)

    return StatsBeingGenerated(stats=stats, features=features, powers=power_selection)


ZombieTemplate: CreatureTemplate = CreatureTemplate(
    name="Zombie",
    tag_line="Relentless Reanimated Corpses",
    description="Zombies are unthinking, reanimated corpses, often gruesomely marred by decay and lethal traumas. They serve whatever supernatural force animates them—typically evil necromancers or fiendish spirits. Zombies are relentless, merciless, and resilient, and their dead flesh can carry on even after suffering grievous wounds.",
    environments=["Planar (Shadowfel)", "Underdark", "Urban"],
    treasure=[],
    variants=[ZombieVariant, ZombieOgreVariant],
    species=[],
    callback=generate_zombie,
)

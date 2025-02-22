import numpy as np

from ..ac_templates import Unarmored
from ..attack_template import weapon
from ..creature_types import CreatureType
from ..damage import DamageType
from ..powers import select_powers
from ..powers.legendary import make_legendary
from ..powers.themed.anti_magic import Spellbreaker
from ..powers.themed.anti_ranged import DeflectMissile
from ..powers.themed.bestial import RetributiveStrike
from ..powers.themed.classes import Barbarian
from ..powers.themed.cruel import BloodiedFrenzy, BrutalCritical
from ..powers.themed.fearsome import FearsomeRoar
from ..powers.themed.reckless import RecklessPowers
from ..role_types import MonsterRole
from ..size import Size
from ..skills import Skills, Stats, StatScaling
from ..utils.interpolate import interpolate_by_cr
from ..utils.rng import choose_enum
from .base_stats import base_stats
from .species import AllSpecies
from .template import (
    CreatureSpecies,
    CreatureTemplate,
    CreatureVariant,
    StatsBeingGenerated,
    SuggestedCr,
)


def custom_weights(p):
    powers = [
        Spellbreaker,
        DeflectMissile,
        RetributiveStrike,
        Barbarian,
        BrutalCritical,
        BloodiedFrenzy,
        FearsomeRoar,
    ] + RecklessPowers

    return 2 if p in powers else 1


BerserkerVariant = CreatureVariant(
    name="Berserker",
    description="Berserkers might fight for personal glory or form motivated forces or howling hordes.",
    suggested_crs=[
        SuggestedCr(name="Berserker", cr=2, srd_creatures=["Berserker"]),
        SuggestedCr(name="Berserker Veteran", cr=4),
    ],
)
CommanderVariant = CreatureVariant(
    name="Berserker Commander",
    description="Berserker commanders bear the scars of battle and drive their followers to match their deadly zeal. These commanders tap into a primal magic to enhance their might.",
    suggested_crs=[
        SuggestedCr(
            name="Berserker Commander",
            cr=8,
            other_creatures={"Berserker Commander": "mm25"},
        ),
        SuggestedCr(name="Berserker Legend", cr=14, is_legendary=True),
    ],
)


def generate_berserker(
    name: str,
    cr: float,
    variant: CreatureVariant,
    species: CreatureSpecies,
    rng: np.random.Generator,
) -> StatsBeingGenerated:
    # STATS
    stats = base_stats(
        name=name,
        cr=cr,
        stats=[
            Stats.STR.scaler(StatScaling.Primary),
            Stats.DEX.scaler(StatScaling.Medium, 2),
            Stats.CON.scaler(StatScaling.Constitution, 2),
            Stats.INT.scaler(StatScaling.Default, mod=-1),
            Stats.WIS.scaler(StatScaling.Default),
            Stats.CHA.scaler(StatScaling.Default, mod=-1),
        ],
    )

    stats = stats.copy(
        creature_type=CreatureType.Humanoid,
        size=Size.Medium,
        languages=["Common"],
        creature_class="Berserker",
    )

    # ARMOR CLASS
    ac_modifier = int(
        interpolate_by_cr(cr, {2: 2, 8: 3, 15: 4})
    )  # based on Berserker and Berserker Commander ACs
    stats = stats.add_ac_template(Unarmored, ac_modifier=ac_modifier)

    # ATTACKS
    attack = weapon.Greataxe
    stats = attack.alter_base_stats(stats, rng)
    stats = attack.initialize_attack(stats)
    stats = stats.copy(primary_damage_type=attack.damage_type)

    # Secondary Damage
    # Berserkers are empowered with primal magic at higher CRs
    elemental_damage_type = choose_enum(rng, list(DamageType.Primal()))
    if cr >= 4:
        stats = stats.copy(secondary_damage_type=elemental_damage_type)

    # ROLES
    stats = stats.with_roles(
        primary_role=MonsterRole.Bruiser,
        additional_roles=[MonsterRole.Leader] if variant is CommanderVariant else [],
    )

    # SKILLS
    stats = stats.grant_proficiency_or_expertise(Skills.Athletics)
    if cr >= 4:
        stats = stats.grant_proficiency_or_expertise(Skills.Perception)
    if cr >= 8:
        stats = stats.grant_proficiency_or_expertise(Skills.Initiative)

    # SAVES
    if cr >= 4:
        stats = stats.copy(
            attributes=stats.attributes.grant_save_proficiency(Stats.STR)
        )

    if cr >= 4:
        stats = stats.copy(
            attributes=stats.attributes.grant_save_proficiency(Stats.CON, Stats.STR)
        )

    # POWERS
    features = []

    # SPECIES CUSTOMIZATIONS
    stats = species.alter_base_stats(stats)

    # ADDITIONAL POWERS
    stats, power_features, power_selection = select_powers(
        stats=stats,
        rng=rng,
        power_level=stats.recommended_powers,
        custom_weights=custom_weights,
    )
    features += power_features

    # FINALIZE
    stats = attack.finalize_attacks(stats, rng)

    # LEGENDARY
    if variant is CommanderVariant:
        stats, features = make_legendary(stats, features, has_lair=False)

    return StatsBeingGenerated(stats=stats, features=features, powers=power_selection)


BerserkerTemplate: CreatureTemplate = CreatureTemplate(
    name="Berserker",
    tag_line="Raging Invaders and Impassioned Warriors",
    description="Gripped by the adrenaline of battle, berserkers are reckless invaders, pit fighters, and other ferocious warriors.",
    environments=["Urban"],
    treasure=["Armaments", "Individual"],
    variants=[BerserkerVariant, CommanderVariant],
    species=AllSpecies,
    callback=generate_berserker,
)

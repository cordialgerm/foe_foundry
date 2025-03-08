from ..ac_templates import BerserkersDefense
from ..attack_template import weapon
from ..creature_types import CreatureType
from ..damage import DamageType
from ..powers import CustomPowerSelection, CustomPowerWeight, Power, select_powers
from ..powers.themed.anti_magic import Spellbreaker
from ..powers.themed.anti_ranged import DeflectMissile
from ..powers.themed.bestial import RetributiveStrike
from ..powers.themed.cruel import BloodiedFrenzy, BrutalCritical
from ..powers.themed.fearsome import FearsomeRoar
from ..powers.themed.reckless import RecklessPowers
from ..role_types import MonsterRole
from ..size import Size
from ..skills import Skills, Stats, StatScaling
from ..utils.rng import choose_enum
from .base_stats import base_stats
from .species import AllSpecies, HumanSpecies
from .template import (
    CreatureTemplate,
    CreatureVariant,
    GenerationSettings,
    StatsBeingGenerated,
    SuggestedCr,
)


class _CustomPowers(CustomPowerSelection):
    def custom_weight(self, power: Power) -> CustomPowerWeight:
        powers = [
            Spellbreaker,
            DeflectMissile,
            RetributiveStrike,
            BrutalCritical,
            BloodiedFrenzy,
            FearsomeRoar,
        ] + RecklessPowers
        if power in powers:
            return CustomPowerWeight(weight=2.0, ignore_usual_requirements=True)
        else:
            return CustomPowerWeight(weight=1.0)


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
        SuggestedCr(name="Berserker Legend", cr=12, is_legendary=True),
    ],
)


def generate_berserker(settings: GenerationSettings) -> StatsBeingGenerated:
    name = settings.creature_name
    cr = settings.cr
    variant = settings.variant
    species = settings.species if settings.species else HumanSpecies
    rng = settings.rng
    is_legendary = settings.is_legendary

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
        hp_multiplier=settings.hp_multiplier,
        damage_multiplier=settings.damage_multiplier,
    )

    stats = stats.copy(
        creature_type=CreatureType.Humanoid,
        size=Size.Medium,
        languages=["Common"],
        creature_class="Berserker",
    )

    # LEGENDARY
    if is_legendary:
        stats = stats.as_legendary()

    # ARMOR CLASS
    stats = stats.add_ac_template(BerserkersDefense)

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
        additional_roles=[MonsterRole.Leader]
        if variant is CommanderVariant
        else [MonsterRole.Soldier],
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
        settings=settings.selection_settings,
        custom=_CustomPowers(),
    )
    features += power_features

    # FINALIZE
    stats = attack.finalize_attacks(stats, rng)

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

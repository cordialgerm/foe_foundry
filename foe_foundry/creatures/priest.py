from ..ac_templates import ChainmailArmor, ChainShirt, PlateArmor
from ..attack_template import spell, weapon
from ..creature_types import CreatureType
from ..damage import DamageType
from ..powers import (
    LOW_POWER,
    MEDIUM_POWER,
    CustomPowerSelection,
    CustomPowerWeight,
    Power,
    PowerType,
    flags,
    select_powers,
)
from ..powers.creature_type import celestial
from ..powers.roles import SupportPowers
from ..powers.spellcaster.celestial import CelestialCasters
from ..powers.themed import holy, technique
from ..role_types import MonsterRole
from ..size import Size
from ..skills import Skills, Stats, StatScaling
from ..spells import CasterType
from ..statblocks import MonsterDials
from .base_stats import BaseStatblock, base_stats
from .species import AllSpecies, HumanSpecies
from .template import (
    CreatureTemplate,
    CreatureVariant,
    GenerationSettings,
    StatsBeingGenerated,
    SuggestedCr,
)

PriestVariant = CreatureVariant(
    name="Priest",
    description="Priests draw on their beliefs to heal the needful and smite their foes. They can channel their faith as spells and empower their weapons with divine might.",
    suggested_crs=[
        SuggestedCr(name="Acolyte", cr=1 / 4, srd_creatures=["Acolyte"]),
        SuggestedCr(name="Priest", cr=2, srd_creatures=["Priest"]),
        SuggestedCr(
            name="Archpriest",
            cr=12,
            other_creatures={"Archpriest": "mm25"},
        ),
        SuggestedCr(name="Archpriest Revered One", cr=16, is_legendary=True),
    ],
)


class _PriestWeights(CustomPowerSelection):
    def __init__(self, stats: BaseStatblock, variant: CreatureVariant):
        self.stats = stats
        self.variant = variant

    def custom_weight(self, p: Power) -> CustomPowerWeight:
        holy_powers = set(holy.HolyPowers)
        holy_powers.discard(holy.MassCureWounds)

        powers = (
            SupportPowers
            + [
                celestial.DivineLaw,
                celestial.WordsOfRighteousness,
                celestial.DivineLaw,
                celestial.RighteousJudgement,
                celestial.AbsoluteConviction,
                celestial.WordsOfRighteousness,
            ]
            + list(holy_powers)
        )

        suppress_powers = [holy.MassCureWounds]  # already in spellcasting

        if self.stats.cr > 2:
            suppress_powers.append(
                holy.WordOfRadiance
            )  # more interesting powers available

        caster_powers = CelestialCasters()

        techniques = [technique.BlindingAttack]

        if p in suppress_powers:
            return CustomPowerWeight(0, ignore_usual_requirements=True)
        elif p in powers:
            return CustomPowerWeight(2.5, ignore_usual_requirements=True)
        elif p in caster_powers:
            return CustomPowerWeight(2.5, ignore_usual_requirements=False)
        elif p in techniques:
            return CustomPowerWeight(1.5, ignore_usual_requirements=True)
        elif p.power_type == PowerType.Species:
            # boost species powers but still respect requirements
            return CustomPowerWeight(2.0, ignore_usual_requirements=False)
        else:
            return CustomPowerWeight(0.75, ignore_usual_requirements=False)


def generate_priest(settings: GenerationSettings) -> StatsBeingGenerated:
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
            Stats.STR.scaler(StatScaling.Medium, mod=2),
            Stats.DEX.scaler(StatScaling.Default),
            Stats.INT.scaler(StatScaling.Default),
            Stats.WIS.scaler(StatScaling.Primary),
            Stats.CHA.scaler(StatScaling.Default),
        ],
        hp_multiplier=settings.hp_multiplier,
        damage_multiplier=settings.damage_multiplier,
    )

    # LEGENDARY
    if is_legendary:
        stats = stats.as_legendary()

    stats = stats.copy(
        creature_type=CreatureType.Humanoid,
        size=Size.Medium,
        languages=["Common"],
        creature_class="Priest",
        caster_type=CasterType.Divine,
    )

    # ARMOR CLASS
    if stats.cr <= 6:
        stats = stats.add_ac_template(ChainShirt)
    elif stats.cr <= 12:
        stats = stats.add_ac_template(ChainmailArmor)
    else:
        stats = stats.add_ac_template(PlateArmor)

    # ATTACKS
    if stats.cr <= 2:
        attack = weapon.MaceAndShield
        secondary_attack = spell.HolyBolt.with_display_name("Radiant Flame")
        secondary_damage_type = DamageType.Radiant
    else:
        attack = spell.HolyBolt.with_display_name("Radiant Flame")
        secondary_attack = None
        secondary_damage_type = DamageType.Radiant

    stats = attack.alter_base_stats(stats)
    stats = attack.initialize_attack(stats)
    stats = stats.copy(
        secondary_damage_type=secondary_damage_type,
        uses_shield=False,
    )

    if secondary_attack is not None:
        stats = secondary_attack.add_as_secondary_attack(stats)

    # Priests are spellcasters and should have fewer attacks
    stats = stats.with_reduced_attacks(reduce_by=1, min_attacks=2)

    # Damage Scaling
    if stats.cr <= 1 / 2:
        stats = stats.apply_monster_dials(
            MonsterDials(attack_damage_multiplier=1.3)
        )  # low CR damage is too low

    # ROLES
    stats = stats.with_roles(
        primary_role=MonsterRole.Support,
    )

    # SKILLS
    stats = stats.grant_proficiency_or_expertise(Skills.Medicine, Skills.Religion)
    if cr >= 2:
        stats = stats.grant_proficiency_or_expertise(Skills.Perception)
    if cr >= 8:
        stats = stats.grant_proficiency_or_expertise(Skills.Initiative, Skills.Insight)

    # SAVES
    if cr >= 8:
        stats = stats.grant_save_proficiency(Stats.STR, Stats.CON, Stats.INT, Stats.WIS)

    # FLAGS
    # priests don't need other healing powers
    stats = stats.with_flags(flags.HAS_HEALING)

    # POWERS
    features = []

    # SPECIES CUSTOMIZATIONS
    stats = species.alter_base_stats(stats)

    # ADDITIONAL POWERS

    # Priests can use more power at higher CRs to keep them interesting
    stats = stats.apply_monster_dials(
        MonsterDials(
            recommended_powers_modifier=LOW_POWER if stats.cr < 2 else MEDIUM_POWER
        )
    )

    stats, power_features, power_selection = select_powers(
        stats=stats,
        rng=rng,
        settings=settings.selection_settings,
        custom=_PriestWeights(stats, variant),
    )
    features += power_features

    # FINALIZE
    stats = attack.finalize_attacks(stats, rng, repair_all=False)
    if secondary_attack is not None:
        stats = secondary_attack.finalize_attacks(stats, rng, repair_all=False)

    return StatsBeingGenerated(stats=stats, features=features, powers=power_selection)


PriestTemplate: CreatureTemplate = CreatureTemplate(
    name="Priest",
    tag_line="Arbiters of the Mortal and the Divine",
    description="Priests harness the power of faith to work miracles. These religious adherents are as diverse as the faiths they follow. Some obey gods and their servants, while others live by age-old creeds. Belief guides priests’ actions and their magic, which they use to shape the world in line with their ideologies.",
    environments=[],
    treasure=["Relics", "Individual"],
    variants=[PriestVariant],
    species=AllSpecies,
    callback=generate_priest,
)

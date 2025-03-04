from ..ac_templates import ChainShirt, PlateArmor, SplintArmor
from ..attack_template import weapon
from ..creature_types import CreatureType
from ..powers import CustomPowerSelection, CustomPowerWeight, Power, select_powers
from ..powers.creature.warrior import MightyLeap, WarriorPowers
from ..powers.legendary import make_legendary
from ..powers.themed.gadget import NetPowers
from ..powers.themed.organized import OrganizedPowers
from ..powers.themed.technique import TechniquePowers
from ..role_types import MonsterRole
from ..size import Size
from ..skills import Skills, Stats, StatScaling
from ..utils.interpolate import interpolate_by_cr
from ..utils.rng import choose_options
from .base_stats import BaseStatblock, base_stats
from .species import AllSpecies, HumanSpecies
from .template import (
    CreatureTemplate,
    CreatureVariant,
    GenerationSettings,
    StatsBeingGenerated,
    SuggestedCr,
)


class _CustomWeights(CustomPowerSelection):
    def __init__(self, stats: BaseStatblock, variant: CreatureVariant):
        self.stats = stats
        self.variant = variant

    def custom_weight(self, p: Power) -> CustomPowerWeight:
        if p is MightyLeap and self.stats.cr <= 7:
            return CustomPowerWeight(
                weight=0
            )  # low-cr warriors don't have a mighty leap - they're too mundane
        elif p in NetPowers:
            return CustomPowerWeight(weight=0)  # warriors don't fight with nets
        elif p in OrganizedPowers or p in WarriorPowers:
            return CustomPowerWeight(weight=1.5, ignore_usual_requirements=True)
        elif p in TechniquePowers:
            # we want to boost techniques, but we can't skip requirements for them
            return CustomPowerWeight(weight=2.5, ignore_usual_requirements=False)
        else:
            return CustomPowerWeight(weight=1.0, ignore_usual_requirements=False)


ShockInfantryVariant = CreatureVariant(
    name="Shock Infantry",
    description="Shock infantry are trainees or rank-and-file troops. They are skilled at contending with commonplace, nonmagical threats head on.",
    suggested_crs=[
        SuggestedCr(
            name="Shock Infantry",
            cr=1 / 8,
            other_creatures={"Warrior Infantry": "mm25"},
        ),
        SuggestedCr(name="Shock Infantry Veteran", cr=3, srd_creatures=["Veteran"]),
    ],
)
LineInfantryVariant = CreatureVariant(
    name="Line Infantry",
    description="Line infantry are rank-and-file troops that hold the line against commonplace, nonmagical threats.",
    suggested_crs=[
        SuggestedCr(
            name="Line Infantry",
            cr=1 / 8,
            other_creatures={"Warrior Infantry": "mm25"},
        ),
        SuggestedCr(name="Line Infantry Veteran", cr=3, srd_creatures=["Veteran"]),
    ],
)
CommanderVariant = CreatureVariant(
    name="Warrior Commander",
    description="Skilled in both combat and leadership, warrior commanders overcome challenges through a combination of martial skill and clever tactics.",
    suggested_crs=[
        SuggestedCr(
            name="Warrior Commander",
            cr=10,
            other_creatures={"Warrior Commander": "mm25"},
        ),
        SuggestedCr(name="Legendary Warrior", cr=16, is_legendary=True),
    ],
)


def generate_warrior(settings: GenerationSettings) -> StatsBeingGenerated:
    name = settings.creature_name
    cr = settings.cr
    variant = settings.variant
    species = settings.species if settings.species else HumanSpecies
    rng = settings.rng

    # STATS

    if variant is CommanderVariant:
        stat_scaling = [
            Stats.STR.scaler(StatScaling.Primary),
            Stats.DEX.scaler(StatScaling.Medium, mod=4),
            Stats.INT.scaler(StatScaling.Default, mod=2),
            Stats.WIS.scaler(StatScaling.Medium, mod=3),
            Stats.CHA.scaler(StatScaling.Default, mod=2),
        ]
    else:
        stat_scaling = [
            Stats.STR.scaler(StatScaling.Primary),
            Stats.DEX.scaler(StatScaling.Medium),
            Stats.INT.scaler(StatScaling.Default, mod=-2),
            Stats.WIS.scaler(StatScaling.Medium, mod=1),
            Stats.CHA.scaler(StatScaling.Default, mod=-2),
        ]

    stats = base_stats(
        name=name,
        cr=cr,
        stats=stat_scaling,
        hp_multiplier=settings.hp_multiplier,
        damage_multiplier=settings.damage_multiplier,
    )

    stats = stats.copy(
        creature_type=CreatureType.Humanoid,
        size=Size.Medium,
        languages=["Common"],
        creature_class="Warrior",
    )

    # ARMOR CLASS
    quality = int(interpolate_by_cr(cr, {8: 0, 10: 1, 15: 2, 20: 3}))
    if stats.cr >= 5:
        stats = stats.add_ac_template(PlateArmor, ac_modifier=quality)
    elif stats.cr >= 3:
        stats = stats.add_ac_template(SplintArmor, ac_modifier=quality)
    else:
        stats = stats.add_ac_template(ChainShirt, ac_modifier=quality)

    # ATTACKS
    if variant is ShockInfantryVariant:
        attack = choose_options(rng, [weapon.Greataxe, weapon.Greatsword, weapon.Maul])
    elif variant is LineInfantryVariant:
        attack = choose_options(
            rng,
            [
                weapon.Polearm,
                weapon.SpearAndShield,
                weapon.SwordAndShield,
            ],
        )
    else:
        # Commander
        attack = weapon.Greatsword

    secondary_attack = weapon.Shortbow if cr <= 1 else weapon.Crossbow

    stats = attack.alter_base_stats(stats, rng)
    stats = attack.initialize_attack(stats)
    stats = stats.copy(primary_damage_type=attack.damage_type)
    stats = secondary_attack.add_as_secondary_attack(stats)

    # ROLES
    if variant is CommanderVariant:
        primary_role = MonsterRole.Soldier
        additional_roles = [MonsterRole.Leader]
    elif variant is ShockInfantryVariant:
        primary_role = MonsterRole.Soldier
        additional_roles = [MonsterRole.Bruiser]
    else:
        primary_role = MonsterRole.Soldier
        additional_roles = [MonsterRole.Defender]

    stats = stats.with_roles(
        primary_role=primary_role,
        additional_roles=additional_roles,
    )

    # SKILLS
    stats = stats.grant_proficiency_or_expertise(Skills.Athletics)
    if cr >= 3:
        stats = stats.grant_proficiency_or_expertise(
            Skills.Perception, Skills.Initiative
        )
    if variant is CommanderVariant:
        stats = stats.grant_proficiency_or_expertise(Skills.Persuasion, Skills.Insight)

    # SAVES
    if cr >= 3:
        stats = stats.grant_save_proficiency(Stats.STR)
    if cr >= 8:
        stats = stats.grant_save_proficiency(Stats.WIS, Stats.DEX, Stats.CON)

    # POWERS
    features = []

    # SPECIES CUSTOMIZATIONS
    stats = species.alter_base_stats(stats)

    # ADDITIONAL POWERS
    stats, power_features, power_selection = select_powers(
        stats=stats,
        rng=rng,
        settings=settings.selection_settings,
        custom=_CustomWeights(stats, variant),
    )
    features += power_features

    # FINALIZE
    stats = attack.finalize_attacks(stats, rng)

    # LEGENDARY
    if variant is CommanderVariant and stats.cr >= 16:
        stats, features = make_legendary(stats, features, has_lair=False)

    return StatsBeingGenerated(stats=stats, features=features, powers=power_selection)


WarriorTemplate: CreatureTemplate = CreatureTemplate(
    name="Warrior",
    tag_line="Offensive and Defensive Infantry",
    description="Warriors are professionals who make a living through their prowess in battle. They might be skilled in using a variety of tactics or trained to take advantage of unusual battlefields. Warriors often work together, whether in armies or in teams with deliberate goals.",
    environments=["Any"],
    treasure=[],
    variants=[LineInfantryVariant, ShockInfantryVariant, CommanderVariant],
    species=AllSpecies,
    callback=generate_warrior,
)

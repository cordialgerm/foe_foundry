from ...ac_templates import StuddedLeatherArmor
from ...attack_template import weapon
from ...creature_types import CreatureType
from ...damage import DamageType
from ...powers import PowerSelection, select_powers
from ...role_types import MonsterRole
from ...size import Size
from ...skills import Skills, Stats, StatScaling
from ...statblocks import MonsterDials
from ...utils.interpolate import interpolate_by_cr
from .._data import (
    GenerationSettings,
    Monster,
    MonsterTemplate,
    MonsterVariant,
    StatsBeingGenerated,
)
from ..base_stats import base_stats
from ..species import AllSpecies, HumanSpecies
from . import powers

SpyVariant = MonsterVariant(
    name="Spy",
    description="Spies gather information and disseminate lies, manipulating people to gain the results the spies' patrons desire. They're trained to manipulate, infiltrate, and—when necessary—escape in a hurry. Many adopt disguises, aliases, or code names to maintain anonymity.",
    monsters=[
        Monster(name="Spy", cr=1, srd_creatures=["Spy"]),
        Monster(name="Elite Spy", cr=4),
    ],
)
SpyMasterVariant = MonsterVariant(
    name="Spy Master",
    description="Spies gather information and disseminate lies, manipulating people to gain the results the spies' patrons desire. They're trained to manipulate, infiltrate, and—when necessary—escape in a hurry. Many adopt disguises, aliases, or code names to maintain anonymity.",
    monsters=[
        Monster(
            name="Spy Master",
            cr=10,
            other_creatures={"Spy Master": "mm25"},
            is_legendary=True,
        ),
    ],
)


def choose_powers(settings: GenerationSettings) -> PowerSelection:
    if settings.monster_key == "spy":
        return PowerSelection(powers.LoadoutSpy)
    elif settings.monster_key == "elite-spy":
        return PowerSelection(powers.LoadoutEliteSpy)
    elif settings.monster_key == "spy-master":
        return PowerSelection(powers.LoadoutSpyMaster)
    else:
        raise ValueError(f"Unknown monster key: {settings.monster_key}")


def generate_spy(settings: GenerationSettings) -> StatsBeingGenerated:
    name = settings.creature_name
    cr = settings.cr
    variant = settings.variant
    species = settings.species if settings.species else HumanSpecies
    rng = settings.rng
    is_legendary = settings.is_legendary

    # STATS
    stats = base_stats(
        name=variant.name,
        variant_key=settings.variant.key,
        template_key=settings.monster_template,
        monster_key=settings.monster_key,
        species_key=species.key,
        cr=cr,
        stats=[
            Stats.STR.scaler(StatScaling.Default),
            Stats.DEX.scaler(StatScaling.Primary),
            Stats.INT.scaler(StatScaling.Medium, mod=0.5),
            Stats.WIS.scaler(StatScaling.Medium, mod=1),
            Stats.CHA.scaler(StatScaling.Medium, mod=1),
        ],
        hp_multiplier=settings.hp_multiplier,
        damage_multiplier=settings.damage_multiplier,
    )

    # LEGENDARY
    if is_legendary:
        stats = stats.as_legendary()

    stats = stats.copy(
        name=name,
        creature_type=CreatureType.Humanoid,
        size=Size.Medium,
        languages=["Common"],
        creature_class="Spy",
        speed=stats.speed.grant_climbing(),
        primary_damage_type=DamageType.Piercing,
    )

    ## HP
    # spies have lower HP than average
    stats = stats.apply_monster_dials(MonsterDials(hp_multiplier=0.85))

    # ARMOR CLASS
    # based off Spy and Spy Master stats
    ac_modifier = int(interpolate_by_cr(cr, {1: 0, 4: 1, 10: 2, 15: 3}))
    if cr >= 4:
        stats = stats.add_ac_template(StuddedLeatherArmor, ac_modifier=ac_modifier)

    # ATTACKS

    # Spies use poison as their secondary damage type
    # This means we want fewer overall attacks but more damage dice that include poison
    stats = stats.copy(
        secondary_damage_type=DamageType.Poison,
    )
    stats = stats.with_reduced_attacks(reduce_by=1 if stats.cr <= 8 else 2)

    # Spies use poisoned Daggers as their primary attack
    attack = weapon.Daggers.with_display_name("Covert Blade")
    stats = attack.alter_base_stats(stats)
    stats = attack.initialize_attack(stats)
    stats = stats.copy(primary_damage_type=attack.damage_type)

    # Spies also have a Hand Crossbow as a secondary attack
    secondary_attack = weapon.HandCrossbow.with_display_name("Concealed Crossbow")
    stats = secondary_attack.add_as_secondary_attack(stats)

    # ROLES
    stats = stats.with_roles(
        primary_role=MonsterRole.Ambusher,
        additional_roles=[
            MonsterRole.Skirmisher,
            MonsterRole.Artillery,
        ],
    )

    # SKILLS
    stats = stats.grant_proficiency_or_expertise(
        Skills.Deception,
        Skills.Insight,
        Skills.Investigation,
        Skills.Perception,
        Skills.SleightOfHand,
        Skills.Stealth,
        Skills.Initiative,
    )

    # EXPERTISE
    if cr >= 6:
        stats = stats.grant_proficiency_or_expertise(
            Skills.Stealth, Skills.Perception, Skills.Initiative
        )

    # SAVES
    if cr >= 6:
        stats = stats.grant_save_proficiency(Stats.DEX, Stats.CON, Stats.INT, Stats.WIS)

    # POWERS
    features = []

    # SPECIES CUSTOMIZATIONS
    stats = species.alter_base_stats(stats)

    # ADDITIONAL POWERS
    stats, power_features, power_selection = select_powers(
        stats=stats,
        rng=rng,
        custom=choose_powers(settings),
    )
    features += power_features

    # FINALIZE
    stats = attack.finalize_attacks(stats, rng, repair_all=False)
    stats = secondary_attack.finalize_attacks(stats, rng, repair_all=False)

    return StatsBeingGenerated(stats=stats, features=features, powers=power_selection)


SpyTemplate: MonsterTemplate = MonsterTemplate(
    name="Spy",
    tag_line="Infiltrators and Informants",
    description="Spies gather information and disseminate lies, manipulating people to gain the results the spies' patrons desire. They're trained to manipulate, infiltrate, and—when necessary—escape in a hurry. Many adopt disguises, aliases, or code names to maintain anonymity.",
    environments=["Urban"],
    treasure=["Any"],
    variants=[SpyVariant, SpyMasterVariant],
    species=AllSpecies,
    callback=generate_spy,
)

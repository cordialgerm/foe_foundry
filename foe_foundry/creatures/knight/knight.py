from ...ac_templates import PlateArmor
from ...attack_template import weapon
from ...creature_types import CreatureType
from ...damage import Condition, DamageType
from ...powers import NewPowerSelection, PowerLoadout, select_powers
from ...powers.species import powers_for_role
from ...role_types import MonsterRole
from ...size import Size
from ...skills import Skills, Stats, StatScaling
from ...spells import CasterType
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

KnightVariant = MonsterVariant(
    name="Knight",
    description="Knights are heavily armored warriors who lead troops in combat and dominate the field of battle.",
    monsters=[
        Monster(name="Knight", cr=3, srd_creatures=["Knight"]),
        Monster(name="Knight of the Realm", cr=6),
        Monster(
            name="Questing Knight",
            cr=12,
            other_creatures={"Questing Knight": "mm25"},
        ),
        Monster(name="Paragon Knight", cr=16, is_legendary=True),
    ],
)


def choose_powers(settings: GenerationSettings) -> NewPowerSelection:
    if settings.species is not None and settings.species is not HumanSpecies:
        species_loadout = PowerLoadout(
            name=f"{settings.species.name} Powers",
            flavor_text=f"{settings.species.name} powers",
            powers=powers_for_role(
                species=settings.species.name,
                role={MonsterRole.Defender, MonsterRole.Soldier, MonsterRole.Bruiser},
            ),
        )
    else:
        species_loadout = None

    if settings.monster_key == "knight":
        return NewPowerSelection(powers.LoadoutKnight, settings.rng, species_loadout)
    elif settings.monster_key == "knight-of-the-realm":
        return NewPowerSelection(
            powers.LoadoutKnightOfTheRealm, settings.rng, species_loadout
        )
    elif settings.monster_key == "questing-knight":
        return NewPowerSelection(
            powers.LoadoutQuestingKnight, settings.rng, species_loadout
        )
    elif settings.monster_key == "paragon-knight":
        return NewPowerSelection(
            powers.LoadoutParagonKnight, settings.rng, species_loadout
        )
    else:
        raise ValueError(f"Unknown knight variant: {settings.monster_key}")


def generate_knight(settings: GenerationSettings) -> StatsBeingGenerated:
    name = settings.creature_name
    cr = settings.cr
    species = settings.species if settings.species else HumanSpecies
    rng = settings.rng
    is_legendary = settings.is_legendary

    # STATS
    stats = base_stats(
        name=name,
        variant_key=settings.variant.key,
        template_key=settings.monster_template,
        monster_key=settings.monster_key,
        species_key=species.key,
        cr=cr,
        stats=[
            Stats.STR.scaler(StatScaling.Primary),
            Stats.DEX.scaler(StatScaling.Default),
            Stats.INT.scaler(StatScaling.Default),
            Stats.WIS.scaler(StatScaling.Medium),
            Stats.CHA.scaler(StatScaling.Medium, mod=2),
        ],
        hp_multiplier=settings.hp_multiplier * (1.1 if cr >= 12 else 1.0),
        damage_multiplier=settings.damage_multiplier,
    )

    # LEGENDARY
    if is_legendary:
        stats = stats.as_legendary()

    stats = stats.copy(
        creature_type=CreatureType.Humanoid,
        size=Size.Medium,
        languages=["Common"],
        creature_class="Knight",
    )

    # ARMOR CLASS
    stats = stats.add_ac_template(PlateArmor)

    # ATTACKS
    if stats.cr >= 12:
        attack = weapon.Greatsword.with_display_name("Oathbound Blade")
    elif stats.cr >= 6:
        attack = weapon.Greatsword.with_display_name("Blessed Blade")
    else:
        attack = weapon.Greatsword

    secondary_damage_type = DamageType.Radiant

    stats = attack.alter_base_stats(stats)
    stats = attack.initialize_attack(stats)
    stats = stats.copy(
        secondary_damage_type=secondary_damage_type,
        uses_shield=False,
    )

    # ROLES
    stats = stats.with_roles(
        primary_role=MonsterRole.Soldier,
        additional_roles=[MonsterRole.Leader, MonsterRole.Support],
    )

    # SPELLCASTING
    if cr >= 6:
        stats = stats.grant_spellcasting(caster_type=CasterType.Divine)

    # SKILLS
    stats = stats.grant_proficiency_or_expertise(Skills.Athletics)
    if cr >= 5:
        stats = stats.grant_proficiency_or_expertise(
            Skills.Perception, Skills.Persuasion, Skills.Initiative
        )

    # SAVES
    stats = stats.grant_save_proficiency(Stats.CON)
    if cr >= 6:
        stats = stats.grant_save_proficiency(Stats.STR, Stats.WIS, Stats.CHA)

    # IMMUNITIES
    if cr >= 6:
        stats = stats.grant_resistance_or_immunity(
            conditions={Condition.Charmed, Condition.Frightened}
        )

    # POWERS
    features = []

    # SPECIES CUSTOMIZATIONS
    stats = species.alter_base_stats(stats)

    stats, power_features, power_selection = select_powers(
        stats=stats,
        rng=rng,
        settings=settings.selection_settings,
        custom=choose_powers(settings),
    )
    features += power_features

    # FINALIZE
    stats = attack.finalize_attacks(stats, rng, repair_all=False)
    return StatsBeingGenerated(stats=stats, features=features, powers=power_selection)


KnightTemplate: MonsterTemplate = MonsterTemplate(
    name="Knight",
    tag_line="Battle Masters and Heroic Wanderers",
    description="Knights are skilled warriors trained for war and tested in battle. Many serve the rulers of a realm, a faith, or an order devoted to a cause.",
    environments=["Urban", "Rural"],
    treasure=["Relics", "Individual"],
    variants=[KnightVariant],
    species=AllSpecies,
    callback=generate_knight,
)

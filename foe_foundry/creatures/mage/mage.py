from ...ac_templates import ArcaneArmor
from ...attack_template import spell
from ...creature_types import CreatureType
from ...powers import NewPowerSelection, flags, select_powers
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
from . import powers

ApprenticeVariant = MonsterVariant(
    name="Apprentice",
    description="Apprentices are young mages who are still learning the ways of magic. They are eager to prove themselves and are often sent on quests or missions to gain experience and knowledge.",
    monsters=[
        Monster(
            name="Mage Neophyte",
            cr=1 / 4,
            other_creatures={"Apprentice Wizard": "motm"},
        ),
        Monster(
            name="Mage Apprentice", cr=2, other_creatures={"Mage Apprentice": "mm25"}
        ),
    ],
)

AbjurerVariant = MonsterVariant(
    name="Abjurer",
    description="Abjurers are mages who specialize in protective spells. They are skilled at creating magical barriers, wards, and other defenses to protect themselves and their allies from harm.",
    monsters=[
        Monster(name="Abjurer Mage Adept", cr=4),
        Monster(name="Abjurer Mage", cr=6, srd_creatures=["Mage"]),
        Monster(name="Abjurer Archmage", cr=12, srd_creatures=["Archmage"]),
        Monster(name="Abjurer Primagus", cr=16, is_legendary=True),
    ],
)

ConjurerVariant = MonsterVariant(
    name="Conjurer",
    description="Conjurers are mages who specialize in summoning creatures and objects from other planes of existence. They can create temporary allies to fight alongside them, or they could use their powers to create magical traps or barriers.",
    monsters=[
        Monster(name="Conjurer Mage Adept", cr=4),
        Monster(name="Conjurer Mage", cr=6, srd_creatures=["Mage"]),
        Monster(name="Conjurer Archmage", cr=12, srd_creatures=["Archmage"]),
        Monster(name="Conjurer Primagus", cr=16, is_legendary=True),
    ],
)

DivinerVariant = MonsterVariant(
    name="Diviner",
    description="Diviners are mages who specialize in seeing the future and uncovering hidden truths. They can use their powers to predict the actions of their enemies, or they could use their insights to uncover secrets and solve mysteries.",
    monsters=[
        Monster(name="Diviner Mage Adept", cr=4),
        Monster(name="Diviner Mage", cr=6, srd_creatures=["Mage"]),
        Monster(name="Diviner Archmage", cr=12, srd_creatures=["Archmage"]),
        Monster(name="Diviner Primagus", cr=16, is_legendary=True),
    ],
)

EnchanterVariant = MonsterVariant(
    name="Enchanter",
    description="Enchanters are mages who specialize in manipulating the minds of others. They can charm, beguile, or dominate other creatures, or they could use their powers to create magical items or artifacts.",
    monsters=[
        Monster(name="Enchanter Mage Adept", cr=4),
        Monster(name="Enchanter Mage", cr=6, srd_creatures=["Mage"]),
        Monster(name="Enchanter Archmage", cr=12, srd_creatures=["Archmage"]),
        Monster(name="Enchanter Primagus", cr=16, is_legendary=True),
    ],
)

IllusionistVariant = MonsterVariant(
    name="Illusionist",
    description="Illusionists are mages who specialize in creating illusions and phantasms. They can create lifelike images, sounds, and other sensory effects to deceive or distract their enemies, or they could use their powers to create magical traps or barriers.",
    monsters=[
        Monster(name="Illusionist Mage Adept", cr=4),
        Monster(name="Illusionist Mage", cr=6, srd_creatures=["Mage"]),
        Monster(name="Illusionist Archmage", cr=12, srd_creatures=["Archmage"]),
        Monster(name="Illusionist Primagus", cr=16, is_legendary=True),
    ],
)

NecromancerVariant = MonsterVariant(
    name="Necromancer",
    description="Necromancers are mages who specialize in death magic. They can raise the dead to serve as their minions, drain the life force from their enemies, or create powerful curses and hexes to bring ruin to their foes.",
    monsters=[
        Monster(name="Necromancer Adept", cr=4),
        Monster(
            name="Necromancer Mage",
            cr=6,
            srd_creatures=["Mage"],
            other_creatures={"Necromancer": "alias"},
        ),
        Monster(name="Necromancer Archmage", cr=12, srd_creatures=["Archmage"]),
        Monster(name="Necromancer Primagus", cr=16, is_legendary=True),
    ],
)

TransmuterVariant = MonsterVariant(
    name="Transmuter",
    description="Transmuters are mages who specialize in changing the properties of objects and creatures. They can turn lead into gold, transform their enemies into harmless creatures, or create powerful elixirs and potions to enhance their own abilities.",
    monsters=[
        Monster(name="Transmuter Mage Adept", cr=4),
        Monster(name="Transmuter Mage", cr=6, srd_creatures=["Mage"]),
        Monster(name="Transmuter Archmage", cr=12, srd_creatures=["Archmage"]),
        Monster(name="Transmuter Primagus", cr=16, is_legendary=True),
    ],
)

PyromancerVariant = MonsterVariant(
    name="Pyromancer",
    description="Pyromancers are mages who specialize in controlling fire. They can create walls of flame, summon fiery meteors, or unleash devastating fireballs to incinerate their enemies",
    monsters=[
        Monster(name="Pyromancer", cr=6, srd_creatures=["Mage"]),
    ],
)

CryomancerVariant = MonsterVariant(
    name="Cryomancer",
    description="Cryomancers are mages who specialize in controlling ice and cold. They can create blizzards, freeze their enemies in place, or summon icy shards to pierce their foes.",
    monsters=[
        Monster(name="Cryomancer", cr=6, srd_creatures=["Mage"]),
    ],
)

ElectromancerVariant = MonsterVariant(
    name="Electromancer",
    description="Electromancers are mages who specialize in controlling electricity and lightning. They can summon bolts of lightning, create electrical storms, or electrify their enemies with powerful shocks.",
    monsters=[
        Monster(name="Electromancer", cr=6, srd_creatures=["Mage"]),
    ],
)

ToximancerVariant = MonsterVariant(
    name="Toximancer",
    description="Toximancers are mages who specialize in controlling poisons and diseases. They can create clouds of toxic gas, infect their enemies with deadly diseases, or summon swarms of poisonous creatures to attack their foes.",
    monsters=[
        Monster(name="Toximancer", cr=6, srd_creatures=["Mage"]),
    ],
)


def choose_powers(settings: GenerationSettings) -> NewPowerSelection:
    if settings.monster_key == "mage-neophyte":
        return NewPowerSelection(powers.LoadoutApprentice, settings.rng)
    elif settings.monster_key == "mage-apprentice":
        return NewPowerSelection(powers.LoadoutApprentice, settings.rng)
    elif settings.monster_key == "abjurer-mage-adept":
        return NewPowerSelection(powers.LoadoutAbjurerAdept, settings.rng)
    elif settings.monster_key == "abjurer-mage":
        return NewPowerSelection(powers.LoadoutAbjurerMage, settings.rng)
    elif settings.monster_key == "abjurer-archmage":
        return NewPowerSelection(powers.LoadoutAbjurerArchmage, settings.rng)
    elif settings.monster_key == "abjurer-primagus":
        return NewPowerSelection(powers.LoadoutAbjurerArchmage, settings.rng)
    elif settings.monster_key == "conjurer-mage-adept":
        return NewPowerSelection(powers.LoadoutConjurerAdept, settings.rng)
    elif settings.monster_key == "conjurer-mage":
        return NewPowerSelection(powers.LoadoutConjurerMage, settings.rng)
    elif settings.monster_key == "conjurer-archmage":
        return NewPowerSelection(powers.LoadoutConjurerArchmage, settings.rng)
    elif settings.monster_key == "conjurer-primagus":
        return NewPowerSelection(powers.LoadoutConjurerArchmage, settings.rng)
    elif settings.monster_key == "diviner-mage-adept":
        return NewPowerSelection(powers.LoadoutDivinerAdept, settings.rng)
    elif settings.monster_key == "diviner-mage":
        return NewPowerSelection(powers.LoadoutDivinerMage, settings.rng)
    elif settings.monster_key == "diviner-archmage":
        return NewPowerSelection(powers.LoadoutDivinerArchmage, settings.rng)
    elif settings.monster_key == "diviner-primagus":
        return NewPowerSelection(powers.LoadoutDivinerArchmage, settings.rng)
    elif settings.monster_key == "enchanter-mage-adept":
        return NewPowerSelection(powers.LoadoutEnchanterAdept, settings.rng)
    elif settings.monster_key == "enchanter-mage":
        return NewPowerSelection(powers.LoadoutEnchanterMage, settings.rng)
    elif settings.monster_key == "enchanter-archmage":
        return NewPowerSelection(powers.LoadoutEnchanterArchmage, settings.rng)
    elif settings.monster_key == "enchanter-primagus":
        return NewPowerSelection(powers.LoadoutEnchanterArchmage, settings.rng)
    elif settings.monster_key == "illusionist-mage-adept":
        return NewPowerSelection(powers.LoadoutIllusionistAdept, settings.rng)
    elif settings.monster_key == "illusionist-mage":
        return NewPowerSelection(powers.LoadoutIllusionistMage, settings.rng)
    elif settings.monster_key == "illusionist-archmage":
        return NewPowerSelection(powers.LoadoutIllusionistArchmage, settings.rng)
    elif settings.monster_key == "illusionist-primagus":
        return NewPowerSelection(powers.LoadoutIllusionistArchmage, settings.rng)
    elif settings.monster_key == "necromancer-adept":
        return NewPowerSelection(powers.LoadoutNecromancerAdept, settings.rng)
    elif settings.monster_key == "necromancer-mage":
        return NewPowerSelection(powers.LoadoutNecromancerMage, settings.rng)
    elif settings.monster_key == "necromancer-archmage":
        return NewPowerSelection(powers.LoadoutNecromancerArchmage, settings.rng)
    elif settings.monster_key == "necromancer-primagus":
        return NewPowerSelection(powers.LoadoutNecromancerArchmage, settings.rng)
    elif settings.monster_key == "transmuter-mage-adept":
        return NewPowerSelection(powers.LoadoutTransmuterAdept, settings.rng)
    elif settings.monster_key == "transmuter-mage":
        return NewPowerSelection(powers.LoadoutTransmuterMage, settings.rng)
    elif settings.monster_key == "transmuter-archmage":
        return NewPowerSelection(powers.LoadoutTransmuterArchmage, settings.rng)
    elif settings.monster_key == "transmuter-primagus":
        return NewPowerSelection(powers.LoadoutTransmuterArchmage, settings.rng)
    elif settings.monster_key == "pyromancer":
        return NewPowerSelection(powers.PyromancerLoadout, settings.rng)
    elif settings.monster_key == "cryomancer":
        return NewPowerSelection(powers.CryomancerLoadout, settings.rng)
    elif settings.monster_key == "electromancer":
        return NewPowerSelection(powers.ElectromancerLoadout, settings.rng)
    elif settings.monster_key == "toximancer":
        return NewPowerSelection(powers.ToximancerLoadout, settings.rng)
    else:
        raise ValueError(f"Unknown mage monster key: {settings.monster_key}")


def generate_mage(settings: GenerationSettings) -> StatsBeingGenerated:
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
            Stats.STR.scaler(StatScaling.Default, mod=-2),
            Stats.DEX.scaler(StatScaling.Default, mod=2),
            Stats.INT.scaler(StatScaling.Primary),
            Stats.WIS.scaler(StatScaling.Medium),
            Stats.CHA.scaler(StatScaling.Default),
        ],
        hp_multiplier=0.85 * settings.hp_multiplier,
        damage_multiplier=1.2 * settings.damage_multiplier,
    )

    # LEGENDARY
    if is_legendary:
        stats = stats.as_legendary(boost_powers=False)
        stats = stats.with_flags(
            flags.HAS_TELEPORT
        )  # archmage has teleport via legendary action

    stats = stats.copy(
        creature_type=CreatureType.Humanoid,
        size=Size.Medium,
        languages=["Common"],
        creature_class="Wizard",
        caster_type=CasterType.Arcane,
        # mages have many bonus actions, reactions, and limited use abilities
        selection_target_args=dict(
            limited_uses_target=-1,
            limited_uses_max=3 if cr <= 11 else 4,
            reaction_target=-1,
            reaction_max=2,
            spellcasting_powers_target=-1,
            spellcasting_powers_max=-1,
            bonus_action_target=-1,
            bonus_action_max=2,
            recharge_target=1,
            recharge_max=1,
        ),
    )

    # SPEED
    if cr >= 12:
        stats = stats.copy(speed=stats.speed.grant_flying())

    # ARMOR CLASS
    stats = stats.add_ac_template(ArcaneArmor)

    # ATTACKS
    if variant is ApprenticeVariant:
        attack = spell.ArcaneBurst.with_display_name("Magic Missile")
        primary_role = MonsterRole.Artillery
        additional_roles = []
    elif variant is AbjurerVariant:
        attack = spell.ArcaneBurst.with_display_name("Runic Blast")
        primary_role = MonsterRole.Controller
        additional_roles = [MonsterRole.Artillery]
    elif variant is ConjurerVariant:
        attack = spell.ArcaneBurst.with_display_name("Conjured Blast")
        primary_role = MonsterRole.Controller
        additional_roles = [MonsterRole.Artillery]
    elif variant is DivinerVariant:
        attack = spell.ArcaneBurst.with_display_name("Time Warp")
        primary_role = MonsterRole.Controller
        additional_roles = [MonsterRole.Artillery]
    elif variant is EnchanterVariant:
        primary_role = MonsterRole.Controller
        additional_roles = [MonsterRole.Artillery]
        attack = spell.Gaze.with_display_name("Mind-Shattering Gaze")
    elif variant is IllusionistVariant:
        primary_role = MonsterRole.Controller
        additional_roles = [MonsterRole.Artillery]
        attack = spell.Gaze.with_display_name("Shred Reality")
    elif variant is NecromancerVariant:
        primary_role = MonsterRole.Controller
        additional_roles = [MonsterRole.Artillery]
        attack = spell.Deathbolt.with_display_name("Necrotic Blast")
    elif variant is TransmuterVariant:
        primary_role = MonsterRole.Controller
        additional_roles = [MonsterRole.Artillery]
        attack = spell.ArcaneBurst.with_display_name("Shred Matter")
    elif variant is PyromancerVariant:
        primary_role = MonsterRole.Artillery
        additional_roles = [MonsterRole.Controller]
        attack = spell.Firebolt
    elif variant is CryomancerVariant:
        primary_role = MonsterRole.Controller
        additional_roles = [MonsterRole.Artillery]
        attack = spell.Frostbolt
    elif variant is ElectromancerVariant:
        primary_role = MonsterRole.Artillery
        additional_roles = [MonsterRole.Controller]
        attack = spell.Shock
    elif variant is ToximancerVariant:
        primary_role = MonsterRole.Controller
        additional_roles = [MonsterRole.Artillery]
        attack = spell.Poisonbolt
    else:
        raise ValueError(f"Unknown variant {variant}")

    stats = attack.alter_base_stats(stats)
    stats = attack.initialize_attack(stats)

    # ROLES
    stats = stats.with_roles(
        primary_role=primary_role, additional_roles=additional_roles
    )

    # SKILLS
    stats = stats.grant_proficiency_or_expertise(Skills.Arcana, Skills.Perception)
    if cr >= 6:
        stats = stats.grant_proficiency_or_expertise(Skills.History)
    if cr >= 12:
        stats = stats.grant_proficiency_or_expertise(Skills.Arcana, Skills.Initiative)

    # SAVES
    if cr >= 6:
        stats = stats.grant_save_proficiency(Stats.WIS, Stats.INT)

    # POWERS
    features = []

    # ADDITIONAL POWERS
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


MageTemplate: MonsterTemplate = MonsterTemplate(
    name="Mage",
    tag_line="Magical Scholars and Spellcasters",
    description="Mages are magical wonder-workers, ranging from spellcasting overlords to reclusive witches. They study mystical secrets and possess insight into monsters, legends, omens, and other lore. Mages often gather allies or hire assistants to aid them in their research or to attain magical might.",
    environments=[],
    treasure=["Arcana", "Individual"],
    variants=[
        ApprenticeVariant,
        AbjurerVariant,
        ConjurerVariant,
        DivinerVariant,
        EnchanterVariant,
        IllusionistVariant,
        NecromancerVariant,
        TransmuterVariant,
        CryomancerVariant,
        PyromancerVariant,
        ElectromancerVariant,
        ToximancerVariant,
    ],
    species=[],
    callback=generate_mage,
)

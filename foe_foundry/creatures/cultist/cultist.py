from foe_foundry.environs import Affinity, Development, ExtraplanarInfluence
from foe_foundry.statblocks import BaseStatblock

from ...ac_templates import PlateArmor, StuddedLeatherArmor, UnholyArmor
from ...attack_template import AttackTemplate, natural, spell, weapon
from ...creature_types import CreatureType
from ...damage import DamageType
from ...powers import PowerSelection
from ...role_types import MonsterRole
from ...size import Size
from ...skills import AbilityScore, Skills, StatScaling
from ...spells import CasterType
from .._template import (
    GenerationSettings,
    Monster,
    MonsterTemplate,
    MonsterVariant,
)
from ..base_stats import base_stats
from . import powers

CultistVariant = MonsterVariant(
    name="Cultist",
    description="Cultists devote themselves to their faith's leaders and otherworldly masters. While this zeal grants cultists no magical powers, it gives them remarkable resolve in the face of threats. Cultists perform much of a cult's mundane work, which might include evangelism, criminal acts, or serving as sacrifices.",
    monsters=[
        Monster(name="Cultist", cr=1 / 8, srd_creatures=["Cultist"]),
        Monster(name="Cultist Fanatic", cr=2, srd_creatures=["Cult Fanatic"]),
        Monster(
            name="Cultist Grand Master",
            cr=10,
            other_creatures={
                "Cultist Hierophant": "mm25",
                "Cult Grand Master": "alias",
            },
        ),
        Monster(
            name="Cultist Exarch",
            cr=14,
            is_legendary=True,
            other_creatures={"Cult Exarch": "alias"},
        ),
    ],
)

AberrantVariant = MonsterVariant(
    name="Aberrant Cultist",
    description="Aberrant cultists pursue mind-bending powers from alien forces.",
    monsters=[
        Monster(
            name="Aberrant Cultist Initiate",
            cr=4,
            other_creatures={"Aberrant Cult Initiate": "alias"},
        ),
        Monster(
            name="Aberrant Cultist", cr=8, other_creatures={"Aberrant Cultist": "mm25"}
        ),
        Monster(
            name="Aberrant Cultist Grand Master",
            cr=14,
            other_creatures={"Aberrant Cult Grand Master": "alias"},
        ),
    ],
)

NecroVariant = MonsterVariant(
    name="Death Cultist",
    description="Death cultists revel in nihilistic forces, embracing them as paths to undeath, multiversal purity, or entropic inevitability. These cultists serve powerful undead beings, apocalyptic prophecies, or immortals with power over death",
    monsters=[
        Monster(
            name="Death Cultist Initiate",
            cr=4,
            other_creatures={"Death Cult Initiate": "alias"},
        ),
        Monster(name="Death Cultist", cr=8, other_creatures={"Death Cultist": "mm25"}),
        Monster(
            name="Death Cultist Grand Master",
            cr=14,
            other_creatures={"Death Cult Grand Master": "alias"},
        ),
    ],
)

FiendVariant = MonsterVariant(
    name="Fiendish Cultist",
    description="Fiend cultists worship fiends or evil deities. They often work to bring ruin to innocents or to summon their sinister patron into the world. Fiend cultists might serve infamous powers such as archdevils and demon lords, or foul immortals",
    monsters=[
        Monster(name="Fiend Cultist Initiate", cr=4),
        Monster(name="Fiend Cultist", cr=8, other_creatures={"Fiend Cultist": "mm25"}),
        Monster(name="Fiend Cultist Grand Master", cr=14),
    ],
)


class _CultistTemplate(MonsterTemplate):
    def choose_powers(self, settings: GenerationSettings) -> PowerSelection:
        # Basic cultist variants
        if settings.monster_key == 'cultist':
            return PowerSelection(powers.LoadoutCultist)
        elif settings.monster_key == 'cultist-fanatic':
            return PowerSelection(powers.LoadoutCultFanatic)
        elif settings.monster_key == 'cultist-grand-master':
            return PowerSelection(powers.LoadoutCultGrandMaster)
        elif settings.monster_key == 'cultist-exarch':
            return PowerSelection(powers.LoadoutCultExarch)
        # Aberrant cultist variants
        elif settings.monster_key == 'aberrant-cultist-initiate':
            return PowerSelection(powers.LoadoutAberrantInitiate)
        elif settings.monster_key == 'aberrant-cultist':
            return PowerSelection(powers.LoadoutAberrantCultist)
        elif settings.monster_key == 'aberrant-cultist-grand-master':
            return PowerSelection(powers.LoadoutAberrantGrandMaster)
        # Death cultist variants
        elif settings.monster_key == 'death-cultist-initiate':
            return PowerSelection(powers.LoadoutDeathCultInitiate)
        elif settings.monster_key == 'death-cultist':
            return PowerSelection(powers.LoadoutDeathCultist)
        elif settings.monster_key == 'death-cultist-grand-master':
            return PowerSelection(powers.LoadoutDeathCultGrandMaster)
        # Fiend cultist variants
        elif settings.monster_key == 'fiend-cultist-initiate':
            return PowerSelection(powers.LoadoutFiendishInitiate)
        elif settings.monster_key == 'fiend-cultist':
            return PowerSelection(powers.LoadoutFiendishCultist)
        elif settings.monster_key == 'fiend-cultist-grand-master':
            return PowerSelection(powers.LoadoutFiendishGrandMaster)
        else:
            raise ValueError(f"Unknown monster_key: {settings.monster_key}")

    def generate_stats(
        self, settings: GenerationSettings
    ) -> tuple[BaseStatblock, list[AttackTemplate]]:
        name = settings.creature_name
        cr = settings.cr
        variant = settings.variant
        is_legendary = settings.is_legendary

        # STATS
        stats = base_stats(
            name=name,
            variant_key=settings.variant.key,
            template_key=settings.monster_template,
            monster_key=settings.monster_key,
            cr=cr,
            stats={
                AbilityScore.STR: (StatScaling.Default, 1),
                AbilityScore.DEX: (StatScaling.Medium, 1),
                AbilityScore.INT: StatScaling.Default,
                AbilityScore.WIS: (StatScaling.Medium, 1),
                AbilityScore.CHA: StatScaling.Primary,
            },
            hp_multiplier=settings.hp_multiplier,
            damage_multiplier=settings.damage_multiplier,
        )

        stats = stats.copy(
            creature_type=CreatureType.Humanoid,
            size=Size.Medium,
            languages=["Common"],
            creature_class="Cultist",
            caster_type=CasterType.Pact,
        )

        # ARMOR CLASS
        if stats.cr <= 2:
            stats = stats.add_ac_template(StuddedLeatherArmor)
        elif variant is FiendVariant:
            stats = stats.add_ac_template(PlateArmor)
        else:
            stats = stats.add_ac_template(UnholyArmor)

        # LEGENDARY
        if is_legendary:
            stats = stats.as_legendary()

        # ATTACKS
        if variant is CultistVariant:
            attack = weapon.Daggers.with_display_name("Ritual Dagger")
            secondary_damage_type = DamageType.Necrotic
        elif variant is AberrantVariant:
            attack = natural.Tentacle.with_display_name("Aberrant Tentacle")
            secondary_damage_type = DamageType.Psychic
        elif variant is NecroVariant:
            attack = spell.Deathbolt.with_display_name("Deathly Ray")
            secondary_damage_type = DamageType.Necrotic
        elif variant is FiendVariant:
            attack = weapon.Greataxe.with_display_name("Infernal Axe")
            secondary_damage_type = DamageType.Fire

        stats = stats.copy(
            secondary_damage_type=secondary_damage_type,
        )

        # ROLES
        additional_roles = []
        primary_role = MonsterRole.Controller
        if cr >= 10:
            additional_roles.append(MonsterRole.Leader)
        if variant is not FiendVariant:
            additional_roles.append(MonsterRole.Artillery)
        if variant is FiendVariant:
            primary_role = MonsterRole.Bruiser
            additional_roles.append(MonsterRole.Controller)

        stats = stats.with_roles(
            primary_role=primary_role,
            additional_roles=additional_roles,
        )

        # SKILLS
        stats = stats.grant_proficiency_or_expertise(Skills.Deception, Skills.Religion)
        if cr >= 2:
            stats = stats.grant_proficiency_or_expertise(Skills.Persuasion)
        if cr >= 8:
            stats = stats.grant_proficiency_or_expertise(Skills.Initiative)

        # SAVES
        if cr >= 2:
            stats = stats.grant_save_proficiency(AbilityScore.WIS)

        return stats, [attack]


CultistTemplate: MonsterTemplate = _CultistTemplate(
    name="Cultist",
    tag_line="Doomsayers and Fanatics",
    description="Cultists use magic and extreme measures to spread radical beliefs. Some privately pursue esoteric secrets, while others form shadowy cabals seeking to bring about terrifying ends. Cultists often follow obscure mystical traditions or obsess over interpretations of ancient prophecies. They might worship supernatural patrons—deities, otherworldly creatures, manipulative alien minds, or stranger forces",
    treasure=["Armaments", "Individual"],
    variants=[CultistVariant, AberrantVariant, NecroVariant, FiendVariant],
    species=[],
    environments=[
        (
            Development.urban,
            Affinity.common,
        ),  # Hidden cells and secret meetings in cities
        (Development.settlement, Affinity.common),  # Infiltrating towns and villages
        (Development.ruin, Affinity.common),  # Ancient sites for forbidden rituals
        (
            Development.dungeon,
            Affinity.uncommon,
        ),  # Underground temples and hidden sanctuaries
        (
            Development.countryside,
            Affinity.uncommon,
        ),  # Remote farmsteads and isolated communities
        (
            ExtraplanarInfluence.hellish,
            Affinity.uncommon,
        ),  # Areas touched by otherworldly forces
        (
            Development.wilderness,
            Affinity.rare,
        ),  # Secret ritual sites far from civilization
    ],
)

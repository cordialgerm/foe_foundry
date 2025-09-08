"""
Comprehensive tag definitions for the Foe Foundry tag system.

This module defines all available tags with their names, descriptions, and icons.
Each tag category is organized into its own section for easy maintenance.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass(frozen=True)
class TagDefinition:
    """Defines a tag with its metadata"""
    name: str
    description: str
    icon: str
    category: str
    
    @property
    def key(self) -> str:
        """Returns a normalized key for the tag"""
        return self.name.lower().replace(" ", "_")


# Creature Type Tags
CREATURE_TYPE_TAGS = [
    TagDefinition("aberration", "Strange and otherworldly creatures", "tentacle-strike.svg", "creature_type"),
    TagDefinition("beast", "Natural animals and creatures", "bear-head.svg", "creature_type"),
    TagDefinition("celestial", "Divine and heavenly creatures", "angel-wings.svg", "creature_type"),
    TagDefinition("construct", "Artificial beings and golems", "robot-golem.svg", "creature_type"),
    TagDefinition("dragon", "Dragons and draconic creatures", "dragon-head.svg", "creature_type"),
    TagDefinition("elemental", "Elemental beings of pure elements", "atom.svg", "creature_type"),
    TagDefinition("fey", "Magical creatures from faerie realm", "fairy.svg", "creature_type"),
    TagDefinition("fiend", "Demonic and devilish creatures", "devil-mask.svg", "creature_type"),
    TagDefinition("giant", "Large humanoid creatures", "giant.svg", "creature_type"),
    TagDefinition("humanoid", "Humans and humanlike creatures", "person.svg", "creature_type"),
    TagDefinition("monstrosity", "Unnatural but not otherworldly creatures", "monster-grasp.svg", "creature_type"),
    TagDefinition("ooze", "Amorphous creatures like slimes", "slime.svg", "creature_type"),
    TagDefinition("plant", "Vegetable creatures", "carnivorous-plant.svg", "creature_type"),
    TagDefinition("undead", "Formerly living creatures", "skull-crossed-bones.svg", "creature_type"),
]

# Monster Role Tags
MONSTER_ROLE_TAGS = [
    TagDefinition("ambusher", "Strikes from hiding or surprise", "ninja-mask.svg", "monster_role"),
    TagDefinition("artillery", "Long-range attackers", "crossbow.svg", "monster_role"),
    TagDefinition("bruiser", "Heavy damage dealers", "muscle-up.svg", "monster_role"),
    TagDefinition("controller", "Battlefield manipulators", "magic-portal.svg", "monster_role"),
    TagDefinition("defender", "Protective tank-like creatures", "shield.svg", "monster_role"),
    TagDefinition("leader", "Command and support others", "crown.svg", "monster_role"),
    TagDefinition("skirmisher", "Mobile hit-and-run fighters", "running-ninja.svg", "monster_role"),
    TagDefinition("support", "Provides assistance to allies", "mailed-fist.svg", "monster_role"),
    TagDefinition("soldier", "Standard combat troops", "sword-brandish.svg", "monster_role"),
    TagDefinition("legendary", "Exceptional boss-tier creatures", "crown-of-thorns.svg", "monster_role"),
]

# Environment - Biome Tags
BIOME_TAGS = [
    TagDefinition("arctic", "Cold, icy regions", "snowflake-1.svg", "biome"),
    TagDefinition("desert", "Hot, dry sandy regions", "cactus.svg", "biome"),
    TagDefinition("forest", "Wooded areas with trees", "tree-branch.svg", "biome"),
    TagDefinition("jungle", "Dense tropical forests", "vine-leaf.svg", "biome"),
    TagDefinition("grassland", "Open grassy plains", "grass.svg", "biome"),
    TagDefinition("farmland", "Cultivated agricultural land", "wheat.svg", "biome"),
    TagDefinition("ocean", "Vast saltwater bodies", "wave-crest.svg", "biome"),
    TagDefinition("river", "Flowing freshwater", "river.svg", "biome"),
    TagDefinition("lake", "Large freshwater bodies", "water-drop.svg", "biome"),
    TagDefinition("swamp", "Wetland marshes", "swamp.svg", "biome"),
    TagDefinition("underground", "Subterranean environments", "cave-entrance.svg", "biome"),
    TagDefinition("extraplanar", "Other-dimensional spaces", "portal.svg", "biome"),
]

# Environment - Terrain Tags
TERRAIN_TAGS = [
    TagDefinition("mountain", "High rocky peaks", "mountain-cave.svg", "terrain"),
    TagDefinition("hill", "Elevated gentle slopes", "hills.svg", "terrain"),
    TagDefinition("plain", "Flat open areas", "horizon-road.svg", "terrain"),
    TagDefinition("water", "Water-covered areas", "water-drop.svg", "terrain"),
]

# Environment - Development Tags
DEVELOPMENT_TAGS = [
    TagDefinition("wilderness", "Natural untamed areas", "tree-growth.svg", "development"),
    TagDefinition("frontier", "Minimal development outposts", "wooden-sign.svg", "development"),
    TagDefinition("countryside", "Rural villages and farms", "village.svg", "development"),
    TagDefinition("settlement", "Established communities", "house.svg", "development"),
    TagDefinition("urban", "Cities and advanced infrastructure", "modern-city.svg", "development"),
    TagDefinition("ruin", "Abandoned destroyed areas", "ancient-ruins.svg", "development"),
    TagDefinition("stronghold", "Fortified military areas", "castle.svg", "development"),
    TagDefinition("dungeon", "Underground hidden areas", "dungeon-gate.svg", "development"),
]

# Environment - Extraplanar Tags
EXTRAPLANAR_TAGS = [
    TagDefinition("astral", "Ethereal dreamlike qualities", "cosmic-egg.svg", "extraplanar"),
    TagDefinition("elemental_plane", "Strong elemental characteristics", "atom.svg", "extraplanar"),
    TagDefinition("faerie", "Magical whimsical qualities", "fairy-wings.svg", "extraplanar"),
    TagDefinition("celestial_plane", "Divine holy characteristics", "holy-symbol.svg", "extraplanar"),
    TagDefinition("hellish", "Dark infernal characteristics", "hell-crosses.svg", "extraplanar"),
    TagDefinition("deathly", "Dark eerie death qualities", "skull-crossed-bones.svg", "extraplanar"),
]

# Damage Type Tags
DAMAGE_TYPE_TAGS = [
    TagDefinition("acid", "Acidic corrosive damage", "acid-blob.svg", "damage_type"),
    TagDefinition("bludgeoning", "Blunt physical damage", "mace-head.svg", "damage_type"),
    TagDefinition("cold", "Freezing ice damage", "ice-cube.svg", "damage_type"),
    TagDefinition("fire", "Burning flame damage", "fire.svg", "damage_type"),
    TagDefinition("force", "Pure magical energy", "magic-swirl.svg", "damage_type"),
    TagDefinition("lightning", "Electrical shock damage", "lightning-arc.svg", "damage_type"),
    TagDefinition("necrotic", "Death and decay damage", "death-skull.svg", "damage_type"),
    TagDefinition("piercing", "Sharp pointed damage", "spear-feather.svg", "damage_type"),
    TagDefinition("poison", "Toxic venomous damage", "poison-bottle.svg", "damage_type"),
    TagDefinition("psychic", "Mental mind damage", "brain-stem.svg", "damage_type"),
    TagDefinition("radiant", "Divine light damage", "sun-radiations.svg", "damage_type"),
    TagDefinition("slashing", "Sharp cutting damage", "sword-slice.svg", "damage_type"),
    TagDefinition("thunder", "Sonic sound damage", "sonic-boom.svg", "damage_type"),
]

# Power Type Tags
POWER_TYPE_TAGS = [
    TagDefinition("attack", "Offensive combat powers", "sword-brandish.svg", "power_type"),
    TagDefinition("defense", "Protective defensive powers", "shield.svg", "power_type"),
    TagDefinition("areaofeffect", "Wide area affecting powers", "explosion-rays.svg", "power_type"),
    TagDefinition("movement", "Mobility and positioning powers", "sprint.svg", "power_type"),
    TagDefinition("debuff", "Weakening enemy powers", "cursed-star.svg", "power_type"),
    TagDefinition("buff", "Strengthening ally powers", "muscle-up.svg", "power_type"),
    TagDefinition("summon", "Creature summoning powers", "magic-portal.svg", "power_type"),
    TagDefinition("environmental", "Environment interaction powers", "earth-spit.svg", "power_type"),
    TagDefinition("aura", "Persistent area effects", "aura.svg", "power_type"),
    TagDefinition("healing", "Health restoration powers", "healing.svg", "power_type"),
    TagDefinition("utility", "Non-combat utility powers", "toolbox.svg", "power_type"),
    TagDefinition("magic", "Magical spell-like powers", "magic-hat.svg", "power_type"),
    TagDefinition("stealth", "Concealment and hiding powers", "hood.svg", "power_type"),
]

# Challenge Rating Tier Tags
CR_TIER_TAGS = [
    TagDefinition("tier0", "Levels 1-2 (CR 0-1/2)", "level-two.svg", "cr_tier"),
    TagDefinition("tier1", "Levels 2-4 (CR 1-3)", "level-two-advanced.svg", "cr_tier"),
    TagDefinition("tier2", "Levels 5-9 (CR 4-12)", "level-three.svg", "cr_tier"),
    TagDefinition("tier3", "Levels 10-14 (CR 13-19)", "level-three-advanced.svg", "cr_tier"),
    TagDefinition("tier4", "Levels 15-20 (CR 20+)", "level-four.svg", "cr_tier"),
]

# Creature Family/Species Tags
CREATURE_FAMILY_TAGS = [
    TagDefinition("balor", "Balor demons", "devil-mask.svg", "creature_family"),
    TagDefinition("basilisk", "Basilisk creatures", "reptile-tail.svg", "creature_family"),
    TagDefinition("bugbear", "Bugbear goblinoids", "goblin-head.svg", "creature_family"),
    TagDefinition("chimera", "Chimera creatures", "griffin-symbol.svg", "creature_family"),
    TagDefinition("cultist", "Cult members", "cultist.svg", "creature_family"),
    TagDefinition("dire_bunny", "Dire bunny creatures", "rabbit-head.svg", "creature_family"),
    TagDefinition("druid", "Druidic characters", "oak-leaf.svg", "creature_family"),
    TagDefinition("frost_giant", "Frost giants", "giant.svg", "creature_family"),
    TagDefinition("gelatinous_cube", "Gelatinous cubes", "cube.svg", "creature_family"),
    TagDefinition("ghoul", "Ghoul undead", "shambling-zombie.svg", "creature_family"),
    TagDefinition("goblin", "Goblin creatures", "goblin-head.svg", "creature_family"),
    TagDefinition("gorgon", "Gorgon creatures", "medusa-head.svg", "creature_family"),
    TagDefinition("guard", "Guard NPCs", "guards.svg", "creature_family"),
    TagDefinition("hydra", "Hydra creatures", "hydra.svg", "creature_family"),
    TagDefinition("knight", "Knight characters", "mounted-knight.svg", "creature_family"),
    TagDefinition("kobold", "Kobold creatures", "goblin-head.svg", "creature_family"),
    TagDefinition("lich", "Lich undead", "evil-book.svg", "creature_family"),
    TagDefinition("mage", "Spellcaster mages", "wizard-staff.svg", "creature_family"),
    TagDefinition("manticore", "Manticore creatures", "griffin-symbol.svg", "creature_family"),
    TagDefinition("merrow", "Merrow creatures", "triton-head.svg", "creature_family"),
    TagDefinition("mimic", "Mimic creatures", "mimic-chest.svg", "creature_family"),
    TagDefinition("nothic", "Nothic creatures", "one-eyed.svg", "creature_family"),
    TagDefinition("ogre", "Ogre creatures", "ogre.svg", "creature_family"),
    TagDefinition("simulacrum", "Simulacrum constructs", "android-mask.svg", "creature_family"),
    TagDefinition("skeletal", "Skeletal undead", "skeleton.svg", "creature_family"),
    TagDefinition("spider", "Spider creatures", "spider-web.svg", "creature_family"),
    TagDefinition("spirit", "Spirit creatures", "ghost.svg", "creature_family"),
    TagDefinition("vrock", "Vrock demons", "harpy.svg", "creature_family"),
    TagDefinition("wight", "Wight undead", "ghost.svg", "creature_family"),
    TagDefinition("wolf", "Wolf creatures", "wolf-head.svg", "creature_family"),
    TagDefinition("zombie", "Zombie undead", "shambling-zombie.svg", "creature_family"),
]

# Thematic Power Tags
THEMATIC_POWER_TAGS = [
    TagDefinition("aberrant", "Strange otherworldly powers", "tentacle-strike.svg", "theme"),
    TagDefinition("anti_magic", "Magic-negating powers", "magic-shield.svg", "theme"),
    TagDefinition("anti_ranged", "Ranged-attack negating powers", "shield-bounces.svg", "theme"),
    TagDefinition("aquatic", "Water-based powers", "wave-crest.svg", "theme"),
    TagDefinition("bestial", "Animal-like powers", "claw-slashes.svg", "theme"),
    TagDefinition("breath", "Breath weapon powers", "dragon-breath.svg", "theme"),
    TagDefinition("chaotic", "Unpredictable random powers", "abstract-050.svg", "theme"),
    TagDefinition("charm", "Mind-influencing powers", "charm.svg", "theme"),
    TagDefinition("clever", "Intelligence-based powers", "brain-stem.svg", "theme"),
    TagDefinition("cowardly", "Fear and retreat powers", "backstab.svg", "theme"),
    TagDefinition("cruel", "Sadistic harmful powers", "serrated-slash.svg", "theme"),
    TagDefinition("cursed", "Curse-based powers", "cursed-star.svg", "theme"),
    TagDefinition("deathly", "Death-themed powers", "death-skull.svg", "theme"),
    TagDefinition("diseased", "Disease and plague powers", "virus.svg", "theme"),
    TagDefinition("domineering", "Control and command powers", "crown.svg", "theme"),
    TagDefinition("earthy", "Earth and stone powers", "stone-pile.svg", "theme"),
    TagDefinition("emanation", "Radiating effect powers", "aura.svg", "theme"),
    TagDefinition("fast", "Speed and haste powers", "fast-arrow.svg", "theme"),
    TagDefinition("fearsome", "Fear-inspiring powers", "screaming.svg", "theme"),
    TagDefinition("flying", "Flight and aerial powers", "wing-cloak.svg", "theme"),
    TagDefinition("gadget", "Tool and device powers", "gear-hammer.svg", "theme"),
    TagDefinition("holy", "Divine blessed powers", "holy-symbol.svg", "theme"),
    TagDefinition("honorable", "Honor-based powers", "mounted-knight.svg", "theme"),
    TagDefinition("hunter", "Tracking and hunting powers", "bow-arrow.svg", "theme"),
    TagDefinition("icy", "Cold and ice powers", "ice-cube.svg", "theme"),
    TagDefinition("illusory", "Illusion and deception powers", "invisible.svg", "theme"),
    TagDefinition("monstrous", "Monstrous creature powers", "monster-grasp.svg", "theme"),
    TagDefinition("petrifying", "Stone transformation powers", "stone-block.svg", "theme"),
    TagDefinition("poisonous", "Toxic and venomous powers", "poison-cloud.svg", "theme"),
    TagDefinition("psionic", "Mental and psionic powers", "psychic-waves.svg", "theme"),
    TagDefinition("reckless", "Wild dangerous powers", "bolt-bomb.svg", "theme"),
    TagDefinition("serpentine", "Snake-like powers", "snake-tongue.svg", "theme"),
    TagDefinition("shamanic", "Shamanic spiritual powers", "totem.svg", "theme"),
    TagDefinition("sneaky", "Stealth and subterfuge powers", "ninja-mask.svg", "theme"),
    TagDefinition("storm", "Weather and storm powers", "lightning-storm.svg", "theme"),
    TagDefinition("technique", "Skill-based martial powers", "sword-smithing.svg", "theme"),
    TagDefinition("teleportation", "Teleportation powers", "teleport.svg", "theme"),
    TagDefinition("temporal", "Time manipulation powers", "time-bomb.svg", "theme"),
    TagDefinition("thuggish", "Brutish criminal powers", "brass-knuckles.svg", "theme"),
    TagDefinition("totemic", "Totemic spiritual powers", "totem-head.svg", "theme"),
    TagDefinition("tough", "Resilience and durability powers", "armor-vest.svg", "theme"),
    TagDefinition("trap", "Trap and snare powers", "box-trap.svg", "theme"),
]

# Spellcaster Theme Tags
SPELLCASTER_THEME_TAGS = [
    TagDefinition("celestial_magic", "Celestial divine magic", "angel-wings.svg", "spellcaster_theme"),
    TagDefinition("conjurer", "Summoning magic", "magic-portal.svg", "spellcaster_theme"),
    TagDefinition("cult_magic", "Cult magic", "cultist.svg", "spellcaster_theme"),
    TagDefinition("divination", "Prophetic magic", "crystal-ball.svg", "spellcaster_theme"),
    TagDefinition("druidic_magic", "Nature magic", "oak-leaf.svg", "spellcaster_theme"),
    TagDefinition("elementalist", "Elemental magic", "elemental.svg", "spellcaster_theme"),
    TagDefinition("enchanter", "Mind magic", "charm.svg", "spellcaster_theme"),
    TagDefinition("fiendish_magic", "Demonic magic", "devil-mask.svg", "spellcaster_theme"),
    TagDefinition("illusionist", "Illusion magic", "invisible.svg", "spellcaster_theme"),
    TagDefinition("arcane_magic", "General arcane magic", "magic-hat.svg", "spellcaster_theme"),
    TagDefinition("metamagic", "Magic-altering magic", "magic-swirl.svg", "spellcaster_theme"),
    TagDefinition("necromancer", "Death magic", "skull-staff.svg", "spellcaster_theme"),
    TagDefinition("oath_magic", "Oath-bound magic", "holy-grail.svg", "spellcaster_theme"),
    TagDefinition("psionic_magic", "Mental psychic magic", "brain-tentacle.svg", "spellcaster_theme"),
    TagDefinition("shaman", "Shamanic spirit magic", "totem.svg", "spellcaster_theme"),
    TagDefinition("transmuter", "Transformation magic", "magic-trick.svg", "spellcaster_theme"),
]

# All tag categories combined
ALL_TAG_DEFINITIONS = (
    CREATURE_TYPE_TAGS + 
    MONSTER_ROLE_TAGS + 
    BIOME_TAGS + 
    TERRAIN_TAGS + 
    DEVELOPMENT_TAGS + 
    EXTRAPLANAR_TAGS + 
    DAMAGE_TYPE_TAGS + 
    POWER_TYPE_TAGS + 
    CR_TIER_TAGS + 
    CREATURE_FAMILY_TAGS + 
    THEMATIC_POWER_TAGS + 
    SPELLCASTER_THEME_TAGS
)

# Create lookup dictionaries
TAG_DEFINITIONS_BY_KEY: Dict[str, TagDefinition] = {tag.key: tag for tag in ALL_TAG_DEFINITIONS}
TAG_DEFINITIONS_BY_CATEGORY: Dict[str, List[TagDefinition]] = {}

for tag in ALL_TAG_DEFINITIONS:
    if tag.category not in TAG_DEFINITIONS_BY_CATEGORY:
        TAG_DEFINITIONS_BY_CATEGORY[tag.category] = []
    TAG_DEFINITIONS_BY_CATEGORY[tag.category].append(tag)


def get_tag_definition(tag_key: str) -> Optional[TagDefinition]:
    """Get a tag definition by its key"""
    return TAG_DEFINITIONS_BY_KEY.get(tag_key)


def get_tags_by_category(category: str) -> List[TagDefinition]:
    """Get all tags in a specific category"""
    return TAG_DEFINITIONS_BY_CATEGORY.get(category, [])


def get_all_categories() -> List[str]:
    """Get all available tag categories"""
    return list(TAG_DEFINITIONS_BY_CATEGORY.keys())
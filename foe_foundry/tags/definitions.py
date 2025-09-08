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
    color: str
    
    @property
    def key(self) -> str:
        """Returns a normalized key for the tag"""
        return self.name.lower().replace(" ", "_")


# Creature Type Tags
CREATURE_TYPE_TAGS = [
    TagDefinition("aberration", "Strange and otherworldly creatures", "tentacle-strike.svg", "creature_type", "#8B5CF6"),
    TagDefinition("beast", "Natural animals and creatures", "bear-head.svg", "creature_type", "#059669"),
    TagDefinition("celestial", "Divine and heavenly creatures", "angel-wings.svg", "creature_type", "#FDE047"),
    TagDefinition("construct", "Artificial beings and golems", "robot-golem.svg", "creature_type", "#6B7280"),
    TagDefinition("dragon", "Dragons and draconic creatures", "dragon-head.svg", "creature_type", "#DC2626"),
    TagDefinition("elemental", "Elemental beings of pure elements", "atom.svg", "creature_type", "#06B6D4"),
    TagDefinition("fey", "Magical creatures from faerie realm", "fairy.svg", "creature_type", "#EC4899"),
    TagDefinition("fiend", "Demonic and devilish creatures", "devil-mask.svg", "creature_type", "#7C2D12"),
    TagDefinition("giant", "Large humanoid creatures", "giant.svg", "creature_type", "#A16207"),
    TagDefinition("humanoid", "Humans and humanlike creatures", "person.svg", "creature_type", "#4F46E5"),
    TagDefinition("monstrosity", "Unnatural but not otherworldly creatures", "monster-grasp.svg", "creature_type", "#7C3AED"),
    TagDefinition("ooze", "Amorphous creatures like slimes", "slime.svg", "creature_type", "#65A30D"),
    TagDefinition("plant", "Vegetable creatures", "carnivorous-plant.svg", "creature_type", "#16A34A"),
    TagDefinition("undead", "Formerly living creatures", "skull-crossed-bones.svg", "creature_type", "#374151"),
]

# Monster Role Tags
MONSTER_ROLE_TAGS = [
    TagDefinition("ambusher", "Strikes from hiding or surprise", "ninja-mask.svg", "monster_role", "#059669"),
    TagDefinition("artillery", "Long-range attackers", "crossbow.svg", "monster_role", "#DC2626"),
    TagDefinition("bruiser", "Heavy damage dealers", "muscle-up.svg", "monster_role", "#B91C1C"),
    TagDefinition("controller", "Battlefield manipulators", "magic-portal.svg", "monster_role", "#7C3AED"),
    TagDefinition("defender", "Protective tank-like creatures", "shield.svg", "monster_role", "#1D4ED8"),
    TagDefinition("leader", "Command and support others", "crown.svg", "monster_role", "#F59E0B"),
    TagDefinition("skirmisher", "Mobile hit-and-run fighters", "running-ninja.svg", "monster_role", "#10B981"),
    TagDefinition("support", "Provides assistance to allies", "mailed-fist.svg", "monster_role", "#8B5CF6"),
    TagDefinition("soldier", "Standard combat troops", "sword-brandish.svg", "monster_role", "#6B7280"),
    TagDefinition("legendary", "Exceptional boss-tier creatures", "crown-of-thorns.svg", "monster_role", "#EAB308"),
]

# Environment - Biome Tags
BIOME_TAGS = [
    TagDefinition("arctic", "Cold, icy regions", "snowflake-1.svg", "biome", "#3B82F6"),
    TagDefinition("desert", "Hot, dry sandy regions", "cactus.svg", "biome", "#F59E0B"),
    TagDefinition("forest", "Wooded areas with trees", "tree-branch.svg", "biome", "#16A34A"),
    TagDefinition("jungle", "Dense tropical forests", "vine-leaf.svg", "biome", "#15803D"),
    TagDefinition("grassland", "Open grassy plains", "grass.svg", "biome", "#65A30D"),
    TagDefinition("farmland", "Cultivated agricultural land", "wheat.svg", "biome", "#A16207"),
    TagDefinition("ocean", "Vast saltwater bodies", "wave-crest.svg", "biome", "#0EA5E9"),
    TagDefinition("river", "Flowing freshwater", "river.svg", "biome", "#06B6D4"),
    TagDefinition("lake", "Large freshwater bodies", "water-drop.svg", "biome", "#0891B2"),
    TagDefinition("swamp", "Wetland marshes", "swamp.svg", "biome", "#059669"),
    TagDefinition("underground", "Subterranean environments", "cave-entrance.svg", "biome", "#78716C"),
    TagDefinition("extraplanar", "Other-dimensional spaces", "portal.svg", "biome", "#8B5CF6"),
]

# Environment - Terrain Tags
TERRAIN_TAGS = [
    TagDefinition("mountain", "High rocky peaks", "mountain-cave.svg", "terrain", "#78716C"),
    TagDefinition("hill", "Elevated gentle slopes", "hills.svg", "terrain", "#A3A3A3"),
    TagDefinition("plain", "Flat open areas", "horizon-road.svg", "terrain", "#84CC16"),
    TagDefinition("water", "Water-covered areas", "water-drop.svg", "terrain", "#0EA5E9"),
]

# Environment - Development Tags
DEVELOPMENT_TAGS = [
    TagDefinition("wilderness", "Natural untamed areas", "tree-growth.svg", "development", "#16A34A"),
    TagDefinition("frontier", "Minimal development outposts", "wooden-sign.svg", "development", "#A16207"),
    TagDefinition("countryside", "Rural villages and farms", "village.svg", "development", "#65A30D"),
    TagDefinition("settlement", "Established communities", "house.svg", "development", "#6B7280"),
    TagDefinition("urban", "Cities and advanced infrastructure", "modern-city.svg", "development", "#374151"),
    TagDefinition("ruin", "Abandoned destroyed areas", "ancient-ruins.svg", "development", "#57534E"),
    TagDefinition("stronghold", "Fortified military areas", "castle.svg", "development", "#1F2937"),
    TagDefinition("dungeon", "Underground hidden areas", "dungeon-gate.svg", "development", "#111827"),
]

# Environment - Extraplanar Tags
EXTRAPLANAR_TAGS = [
    TagDefinition("astral", "Ethereal dreamlike qualities", "cosmic-egg.svg", "extraplanar", "#A855F7"),
    TagDefinition("elemental_plane", "Strong elemental characteristics", "atom.svg", "extraplanar", "#06B6D4"),
    TagDefinition("faerie", "Magical whimsical qualities", "fairy-wings.svg", "extraplanar", "#EC4899"),
    TagDefinition("celestial_plane", "Divine holy characteristics", "holy-symbol.svg", "extraplanar", "#FDE047"),
    TagDefinition("hellish", "Dark infernal characteristics", "hell-crosses.svg", "extraplanar", "#7C2D12"),
    TagDefinition("deathly", "Dark eerie death qualities", "skull-crossed-bones.svg", "extraplanar", "#374151"),
]

# Damage Type Tags
DAMAGE_TYPE_TAGS = [
    TagDefinition("acid", "Acidic corrosive damage", "acid-blob.svg", "damage_type", "#22C55E"),
    TagDefinition("cold", "Freezing ice damage", "ice-cube.svg", "damage_type", "#3B82F6"),
    TagDefinition("fire", "Burning flame damage", "fire.svg", "damage_type", "#EF4444"),
    TagDefinition("force", "Pure magical energy", "magic-swirl.svg", "damage_type", "#E5E7EB"),
    TagDefinition("lightning", "Electrical shock damage", "lightning-arc.svg", "damage_type", "#06B6D4"),
    TagDefinition("necrotic", "Death and decay damage", "death-skull.svg", "damage_type", "#6B21A8"),
    TagDefinition("poison", "Toxic venomous damage", "poison-bottle.svg", "damage_type", "#15803D"),
    TagDefinition("psychic", "Mental mind damage", "brain-stem.svg", "damage_type", "#A855F7"),
    TagDefinition("radiant", "Divine light damage", "sun-radiations.svg", "damage_type", "#FDE047"),
    TagDefinition("thunder", "Sonic sound damage", "sonic-boom.svg", "damage_type", "#F97316"),
]

# Power Type Tags
POWER_TYPE_TAGS = [
    TagDefinition("attack", "Offensive combat powers", "sword-brandish.svg", "power_type", "#DC2626"),
    TagDefinition("defense", "Protective defensive powers", "shield.svg", "power_type", "#1D4ED8"),
    TagDefinition("areaofeffect", "Wide area affecting powers", "explosion-rays.svg", "power_type", "#F97316"),
    TagDefinition("movement", "Mobility and positioning powers", "sprint.svg", "power_type", "#10B981"),
    TagDefinition("debuff", "Weakening enemy powers", "cursed-star.svg", "power_type", "#7C2D12"),
    TagDefinition("buff", "Strengthening ally powers", "muscle-up.svg", "power_type", "#059669"),
    TagDefinition("summon", "Creature summoning powers", "magic-portal.svg", "power_type", "#8B5CF6"),
    TagDefinition("environmental", "Environment interaction powers", "earth-spit.svg", "power_type", "#A16207"),
    TagDefinition("aura", "Persistent area effects", "aura.svg", "power_type", "#EC4899"),
    TagDefinition("healing", "Health restoration powers", "healing.svg", "power_type", "#16A34A"),
    TagDefinition("utility", "Non-combat utility powers", "toolbox.svg", "power_type", "#6B7280"),
    TagDefinition("magic", "Magical spell-like powers", "magic-hat.svg", "power_type", "#7C3AED"),
    TagDefinition("stealth", "Concealment and hiding powers", "hood.svg", "power_type", "#374151"),
]

# Challenge Rating Tier Tags
CR_TIER_TAGS = [
    TagDefinition("tier0", "Levels 1-2 (CR 0-1/2)", "level-two.svg", "cr_tier", "#FDE047"),
    TagDefinition("tier1", "Levels 2-4 (CR 1-3)", "level-two-advanced.svg", "cr_tier", "#FACC15"),
    TagDefinition("tier2", "Levels 5-9 (CR 4-12)", "level-three.svg", "cr_tier", "#EAB308"),
    TagDefinition("tier3", "Levels 10-14 (CR 13-19)", "level-three-advanced.svg", "cr_tier", "#CA8A04"),
    TagDefinition("tier4", "Levels 15-20 (CR 20+)", "level-four.svg", "cr_tier", "#A16207"),
]

# Creature Family/Species Tags
CREATURE_FAMILY_TAGS = [
    TagDefinition("balor", "Balor demons", "devil-mask.svg", "creature_family", "#DC2626"),
    TagDefinition("basilisk", "Basilisk creatures", "reptile-tail.svg", "creature_family", "#059669"),
    TagDefinition("bugbear", "Bugbear goblinoids", "goblin-head.svg", "creature_family", "#A16207"),
    TagDefinition("chimera", "Chimera creatures", "griffin-symbol.svg", "creature_family", "#B45309"),
    TagDefinition("cultist", "Cult members", "cultist.svg", "creature_family", "#7C2D12"),
    TagDefinition("dire_bunny", "Dire bunny creatures", "rabbit-head.svg", "creature_family", "#92400E"),
    TagDefinition("dragon_family", "Dragon creatures", "dragon-head.svg", "creature_family", "#DC2626"),
    TagDefinition("druid", "Druidic characters", "oak-leaf.svg", "creature_family", "#16A34A"),
    TagDefinition("frost_giant", "Frost giants", "giant.svg", "creature_family", "#3B82F6"),
    TagDefinition("gelatinous_cube", "Gelatinous cubes", "cube.svg", "creature_family", "#22C55E"),
    TagDefinition("ghoul", "Ghoul undead", "shambling-zombie.svg", "creature_family", "#374151"),
    TagDefinition("goblin", "Goblin creatures", "goblin-head.svg", "creature_family", "#CA8A04"),
    TagDefinition("gorgon", "Gorgon creatures", "medusa-head.svg", "creature_family", "#059669"),
    TagDefinition("guard", "Guard NPCs", "guards.svg", "creature_family", "#6B7280"),
    TagDefinition("hydra", "Hydra creatures", "hydra.svg", "creature_family", "#0891B2"),
    TagDefinition("knight", "Knight characters", "mounted-knight.svg", "creature_family", "#1D4ED8"),
    TagDefinition("kobold", "Kobold creatures", "goblin-head.svg", "creature_family", "#F59E0B"),
    TagDefinition("lich", "Lich undead", "evil-book.svg", "creature_family", "#6B21A8"),
    TagDefinition("mage", "Spellcaster mages", "wizard-staff.svg", "creature_family", "#7C3AED"),
    TagDefinition("manticore", "Manticore creatures", "griffin-symbol.svg", "creature_family", "#EA580C"),
    TagDefinition("merrow", "Merrow creatures", "triton-head.svg", "creature_family", "#0EA5E9"),
    TagDefinition("mimic", "Mimic creatures", "mimic-chest.svg", "creature_family", "#A16207"),
    TagDefinition("nothic", "Nothic creatures", "one-eyed.svg", "creature_family", "#8B5CF6"),
    TagDefinition("ogre", "Ogre creatures", "ogre.svg", "creature_family", "#78716C"),
    TagDefinition("simulacrum", "Simulacrum constructs", "android-mask.svg", "creature_family", "#6B7280"),
    TagDefinition("skeletal", "Skeletal undead", "skeleton.svg", "creature_family", "#E5E7EB"),
    TagDefinition("spider", "Spider creatures", "spider-web.svg", "creature_family", "#111827"),
    TagDefinition("spirit", "Spirit creatures", "ghost.svg", "creature_family", "#C084FC"),
    TagDefinition("vrock", "Vrock demons", "harpy.svg", "creature_family", "#B91C1C"),
    TagDefinition("wight", "Wight undead", "ghost.svg", "creature_family", "#9CA3AF"),
    TagDefinition("wolf", "Wolf creatures", "wolf-head.svg", "creature_family", "#57534E"),
    TagDefinition("zombie", "Zombie undead", "shambling-zombie.svg", "creature_family", "#1F2937"),
]

# Thematic Power Tags
THEMATIC_POWER_TAGS = [
    TagDefinition("aberrant", "Strange otherworldly powers", "tentacle-strike.svg", "theme", "#8B5CF6"),
    TagDefinition("anti_magic", "Magic-negating powers", "magic-shield.svg", "theme", "#374151"),
    TagDefinition("anti_ranged", "Ranged-attack negating powers", "shield-bounces.svg", "theme", "#6B7280"),
    TagDefinition("aquatic", "Water-based powers", "wave-crest.svg", "theme", "#0EA5E9"),
    TagDefinition("bestial", "Animal-like powers", "claw-slashes.svg", "theme", "#A16207"),
    TagDefinition("breath", "Breath weapon powers", "dragon-breath.svg", "theme", "#EF4444"),
    TagDefinition("chaotic", "Unpredictable random powers", "abstract-050.svg", "theme", "#EC4899"),
    TagDefinition("charm", "Mind-influencing powers", "charm.svg", "theme", "#F97316"),
    TagDefinition("clever", "Intelligence-based powers", "brain-stem.svg", "theme", "#3B82F6"),
    TagDefinition("cowardly", "Fear and retreat powers", "backstab.svg", "theme", "#78716C"),
    TagDefinition("cruel", "Sadistic harmful powers", "serrated-slash.svg", "theme", "#7C2D12"),
    TagDefinition("cursed", "Curse-based powers", "cursed-star.svg", "theme", "#6B21A8"),
    TagDefinition("deathly_theme", "Death-themed powers", "death-skull.svg", "theme", "#374151"),
    TagDefinition("diseased", "Disease and plague powers", "virus.svg", "theme", "#059669"),
    TagDefinition("domineering", "Control and command powers", "crown.svg", "theme", "#EAB308"),
    TagDefinition("earthy", "Earth and stone powers", "stone-pile.svg", "theme", "#92400E"),
    TagDefinition("emanation", "Radiating effect powers", "aura.svg", "theme", "#A855F7"),
    TagDefinition("fast", "Speed and haste powers", "fast-arrow.svg", "theme", "#10B981"),
    TagDefinition("fearsome", "Fear-inspiring powers", "screaming.svg", "theme", "#B91C1C"),
    TagDefinition("flying", "Flight and aerial powers", "wing-cloak.svg", "theme", "#06B6D4"),
    TagDefinition("gadget", "Tool and device powers", "gear-hammer.svg", "theme", "#6B7280"),
    TagDefinition("holy", "Divine blessed powers", "holy-symbol.svg", "theme", "#FDE047"),
    TagDefinition("honorable", "Honor-based powers", "mounted-knight.svg", "theme", "#1D4ED8"),
    TagDefinition("hunter", "Tracking and hunting powers", "bow-arrow.svg", "theme", "#059669"),
    TagDefinition("icy", "Cold and ice powers", "ice-cube.svg", "theme", "#3B82F6"),
    TagDefinition("illusory", "Illusion and deception powers", "invisible.svg", "theme", "#C084FC"),
    TagDefinition("monstrous", "Monstrous creature powers", "monster-grasp.svg", "theme", "#7C3AED"),
    TagDefinition("petrifying", "Stone transformation powers", "stone-block.svg", "theme", "#78716C"),
    TagDefinition("poisonous", "Toxic and venomous powers", "poison-cloud.svg", "theme", "#15803D"),
    TagDefinition("psionic", "Mental and psionic powers", "psychic-waves.svg", "theme", "#A855F7"),
    TagDefinition("reckless", "Wild dangerous powers", "bolt-bomb.svg", "theme", "#DC2626"),
    TagDefinition("serpentine", "Snake-like powers", "snake-tongue.svg", "theme", "#22C55E"),
    TagDefinition("shamanic", "Shamanic spiritual powers", "totem.svg", "theme", "#A16207"),
    TagDefinition("sneaky", "Stealth and subterfuge powers", "ninja-mask.svg", "theme", "#374151"),
    TagDefinition("spellcaster", "Magical spellcasting abilities", "wizard-staff.svg", "theme", "#7C3AED"),
    TagDefinition("storm", "Weather and storm powers", "lightning-storm.svg", "theme", "#06B6D4"),
    TagDefinition("technique", "Skill-based martial powers", "sword-smithing.svg", "theme", "#6B7280"),
    TagDefinition("teleportation", "Teleportation powers", "teleport.svg", "theme", "#8B5CF6"),
    TagDefinition("temporal", "Time manipulation powers", "time-bomb.svg", "theme", "#8B5CF6"),
    TagDefinition("thuggish", "Brutish criminal powers", "brass-knuckles.svg", "theme", "#78716C"),
    TagDefinition("totemic", "Totemic spiritual powers", "totem-head.svg", "theme", "#A16207"),
    TagDefinition("tough", "Resilience and durability powers", "armor-vest.svg", "theme", "#6B7280"),
    TagDefinition("trap", "Trap and snare powers", "box-trap.svg", "theme", "#7C2D12"),
]

# Spellcaster Theme Tags
SPELLCASTER_THEME_TAGS = [
    TagDefinition("celestial_magic", "Celestial divine magic", "angel-wings.svg", "spellcaster_theme", "#FDE047"),
    TagDefinition("conjurer", "Summoning magic", "magic-portal.svg", "spellcaster_theme", "#8B5CF6"),
    TagDefinition("cult_magic", "Cult magic", "cultist.svg", "spellcaster_theme", "#7C2D12"),
    TagDefinition("divination", "Prophetic magic", "crystal-ball.svg", "spellcaster_theme", "#06B6D4"),
    TagDefinition("druidic_magic", "Nature magic", "oak-leaf.svg", "spellcaster_theme", "#16A34A"),
    TagDefinition("elementalist", "Elemental magic", "elemental.svg", "spellcaster_theme", "#06B6D4"),
    TagDefinition("enchanter", "Mind magic", "charm.svg", "spellcaster_theme", "#EC4899"),
    TagDefinition("fiendish_magic", "Demonic magic", "devil-mask.svg", "spellcaster_theme", "#7C2D12"),
    TagDefinition("illusionist", "Illusion magic", "invisible.svg", "spellcaster_theme", "#C084FC"),
    TagDefinition("arcane_magic", "General arcane magic", "magic-hat.svg", "spellcaster_theme", "#7C3AED"),
    TagDefinition("metamagic", "Magic-altering magic", "magic-swirl.svg", "spellcaster_theme", "#A855F7"),
    TagDefinition("necromancer", "Death magic", "skull-staff.svg", "spellcaster_theme", "#374151"),
    TagDefinition("oath_magic", "Oath-bound magic", "holy-grail.svg", "spellcaster_theme", "#1D4ED8"),
    TagDefinition("psionic_magic", "Mental psychic magic", "brain-tentacle.svg", "spellcaster_theme", "#A855F7"),
    TagDefinition("shaman", "Shamanic spirit magic", "totem.svg", "spellcaster_theme", "#A16207"),
    TagDefinition("transmuter", "Transformation magic", "magic-trick.svg", "spellcaster_theme", "#10B981"),
]

# Size Tags
SIZE_TAGS = [
    TagDefinition("tiny", "Tiny sized creatures", "resize-down.svg", "size", "#9CA3AF"),
    TagDefinition("small", "Small sized creatures", "minions.svg", "size", "#6B7280"), 
    TagDefinition("medium", "Medium sized creatures", "person.svg", "size", "#4B5563"),
    TagDefinition("large", "Large sized creatures", "giant.svg", "size", "#374151"),
    TagDefinition("huge", "Huge sized creatures", "giant.svg", "size", "#1F2937"),
    TagDefinition("gargantuan", "Gargantuan sized creatures", "giant.svg", "size", "#111827"),
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
    SPELLCASTER_THEME_TAGS +
    SIZE_TAGS
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
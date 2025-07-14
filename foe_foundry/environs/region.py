from dataclasses import dataclass

from .biome import Biome
from .development import Development
from .extraplanar import ExtraplanarInfluence
from .terrain import Terrain
from .tiers import Tiers


@dataclass(kw_only=True)
class Region:
    """An area of the world with specific biomes, terrains, development, or extraplanar influence.

    Regions are used to define the environment and locations in which a monster or an NPC can be found.
    Regions can consist of combinations of one or more biomes, terrians, development levels, or extraplanar influence.
    If a property is set to None, then it means that property is not relevant to defining the region.
    If a property contains multiple values, then any of those values are valid for the region
    """

    name: str  # the name of the region
    description: str
    features: list[str]
    weather: list[str]
    tiers: list[Tiers]
    biomes: set[Biome] | None = None  # the natural biomes present in the region
    terrains: set[Terrain] | None = None  # the natural terrains present in the region
    development: set[Development] | None = (
        None  # the level of development, from current or past civilization
    )
    extraplanar_influence: set[ExtraplanarInfluence] | None = (
        None  # the extraplanar influence present in the region
    )


# These regions are defined by the A5E rules, and are used to define the environment in which a monster or an NPC can be found.
### PLACE NEW ENVIRONMENTS BELOW THIS LINE ###

# Alphabetically ordered region objects
BlastedBadlands = Region(
    name="Blasted Badlands",
    description="These deserts are notorious for their many capricious ruins, the devastated landscape the biggest mark left upon the world by the forgotten civilizations that once flourished there. Monsters aplenty roam the wastes as well, so adventurers journeying through it encounter many creatures and constructed terrain exploration challenges.",
    features=[
        "desert",
        "laboratory",
        "mountains",
        "ruins",
        "subterranean",
        "swamp",
        "temple",
        "tomb",
    ],
    tiers=[Tiers.tier_2, Tiers.tier_3, Tiers.tier_4],
    weather=["clear", "overcast", "scorching"],
    biomes={Biome.desert},
    terrains={Terrain.plain, Terrain.hill},
    development={Development.wilderness, Development.ruin, Development.frontier},
)


# Country Shire region definition
CountryShire = Region(
    name="Country Shire",
    description="Small villages and rural communities, often surrounded by a patchwork of farms, make for a safe and cozy existence with the most threatening events involving an angry bear harassing livestock. Adventurers journeying through this region can expect little danger, and a high number of social encounters.",
    features=[
        "forest",
        "grassland",
        "hills",
        "settlement",
        "subterranean",
        "swamp",
        "temple",
    ],
    tiers=[Tiers.tier_0, Tiers.tier_1],
    weather=[
        "clear",
        "overcast",
        "rain",
        "mist",
        "snow",
    ],
    biomes={
        Biome.forest,
        Biome.grassland,
        Biome.farmland,
        Biome.swamp,
        Biome.underground,
    },
    terrains={Terrain.hill, Terrain.plain},
    development={Development.countryside, Development.settlement, Development.frontier},
)


Feywood = Region(
    name="Feywood",
    description="Home to faeries, sprites, dryads, nymphs, satyrs, and other fey, the animals in this forest are bold and only foolish travelers fail to respect nature as they go along their way. Adventurers journeying through regions like this contend with frequent combat encounters, social encounters, and natural terrain and supernatural exploration challenges.",
    features=[
        "forest",
        "grassland",
        "hills",
        "jungle",
        "mountains",
        "ruins",
        "settlement",
        "subterranean",
        "swamp",
        "temple",
        "tomb",
    ],
    tiers=[Tiers.tier_1, Tiers.tier_2, Tiers.tier_3, Tiers.tier_4],
    weather=[
        "clear",
        "mist",
        "rain",
    ],
    biomes={
        Biome.forest,
        Biome.grassland,
        Biome.jungle,
        Biome.swamp,
        Biome.underground,
    },
    terrains={Terrain.hill, Terrain.mountain, Terrain.plain},
    development={Development.settlement, Development.frontier, Development.ruin},
    extraplanar_influence={ExtraplanarInfluence.faerie},
)


FieryHellscape = Region(
    name="Fiery Hellscape",
    description="From active volcanoes to the hottest layers of Hell, these regions are dominated by red-hot lava flows and flaming geysers. Adventurers journeying through these regions can expect to encounter many natural terrain challenges and dangerous creatures.",
    features=[
        "desert",
        "laboratory",
        "mountains",
        "ruins",
        "subterranean",
        "temple",
        "tomb",
    ],
    tiers=[Tiers.tier_3, Tiers.tier_4],
    weather=["uncomfortably warm"],
    biomes={Biome.desert, Biome.underground},
    terrains={Terrain.mountain, Terrain.plain},
    development={Development.ruin, Development.stronghold},
    extraplanar_influence={ExtraplanarInfluence.hellish},
)

FlowingRiver = Region(
    name="Flowing River",
    description="Rivers can provide a convenient and fast way to travel. Encounters are less frequent, and the journey is less arduous.",
    features=[
        "river",
    ],
    tiers=[Tiers.tier_0, Tiers.tier_1, Tiers.tier_2],
    weather=[
        "clear",
        "overcast",
        "rain",
        "mist",
        "snow",
    ],
    biomes={Biome.river},
    terrains=None,  # Any terrain, as rivers cross multiple regions
    development=None,  # Not specific to development
)

FrozenWastes = Region(
    name="Frozen Wastes",
    description="Endless fields of white and imposing mountains stretching towards the sky fill this icy land, and though it is rather devoid of life it is a place of great peril. Adventurers journeying through this region have to overcome many natural terrain and weather event exploration challenges, and perhaps a few combat or social encounters.",
    features=[
        "arctic",
        "hills",
        "mountains",
        "ruins",
        "subterranean",
        "temple",
        "tomb",
        "water",
    ],
    tiers=[Tiers.tier_2, Tiers.tier_3, Tiers.tier_4],
    weather=[
        "clear",
        "overcast",
        "snow",
    ],
    biomes={Biome.arctic},
    terrains={Terrain.hill, Terrain.mountain},
    development={Development.ruin},
)

HauntedLands = Region(
    name="Haunted Lands",
    description="Settlements that have suffered a curse, or areas which are home to powerful undead beings, typically have effects that spread far from the source bringing woe to the people living nearby and attracting prowling monsters and ominous signs. Adventurers journeying through regions like this have plenty of combat encounters, some social encounters, and many circumstance or supernatural exploration challenges.",
    features=[
        "any",
    ],
    tiers=[Tiers.tier_3, Tiers.tier_4],
    weather=[
        "clear",
        "overcast",
        "foggy",
        "rain",
    ],
    biomes=None,  # Any biome
    terrains=None,  # Any terrain
    development={
        Development.ruin,
        Development.countryside,
        Development.frontier,
        Development.settlement,
    },  # haunted countryside, villages, and ruins
    extraplanar_influence={ExtraplanarInfluence.deathly},
)

LoftyMountains = Region(
    name="Lofty Mountains",
    description="Legends from all over the realm speak of remote passes, cataclysmic conflicts and relics of fell power within the ancient ruins of temples to defeated evils, the graves of terrible warlords, and sites of unspeakable rituals. Adventurers journeying through this region have few social encounters, a moderate amount of combat encounters, and many constructed terrain, natural terrain, and supernatural exploration challenges.",
    features=[
        "arctic",
        "hills",
        "jungle",
        "mountains",
        "ruins",
        "settlement",
        "subterranean",
        "temple",
        "tomb",
    ],
    tiers=[Tiers.tier_1, Tiers.tier_2, Tiers.tier_3, Tiers.tier_4],
    weather=[
        "clear",
        "overcast",
        "mist",
        "rain",
        "snow",
    ],
    biomes={Biome.arctic, Biome.jungle, Biome.underground},
    terrains={Terrain.mountain},
    development={
        Development.ruin,
        Development.settlement,
        Development.wilderness,
        Development.frontier,
    },
)

OpenRoads = Region(
    name="Open Roads",
    description="Well-traveled roads with wide tracks, and plentiful inns, villages, and other stopping points along the way make some journeys less arduous than others. Adventurers journeying along country roads have many social encounters, combat encounters with NPCs or the occasional wild beast, and circumstance and constructed terrain exploration challenges.",
    features=[
        "road",
    ],
    tiers=[Tiers.tier_0, Tiers.tier_1, Tiers.tier_2],
    weather=[
        "clear",
        "overcast",
        "rain",
        "mist",
        "snow",
    ],
    biomes=None,  # Any biome
    terrains={Terrain.plain, Terrain.hill},  # Any terrain
    development={
        Development.countryside,
        Development.settlement,
        Development.frontier,
        Development.urban,
    },
)

ParchedSands = Region(
    name="Parched Sands",
    description="Endless dunes and the baking sun make these deserts difficult and dangerous places in which to survive. Adventurers journeying through this region have very few social encounters.",
    features=[
        "desert",
        "grassland",
        "hills",
        "mountains",
        "ruins",
        "settlement",
        "subterranean",
        "temple",
        "tomb",
    ],
    tiers=[Tiers.tier_1, Tiers.tier_2, Tiers.tier_3, Tiers.tier_4],
    weather=["clear"],
    biomes={Biome.desert},
    terrains={Terrain.hill, Terrain.mountain, Terrain.plain},
    development={
        Development.ruin,
        Development.frontier,
        Development.wilderness,
    },
)

RestlessSea = Region(
    name="Restless Sea",
    description="Rapid currents and quick trade routes make these waters popular with merchants, but only the bravest and most skilled sailors are willing to chance the frequent, dangerous, and unpredictable waves. Adventurers journeying through this region or along its coast have to overcome an unusually high number of weather event exploration challenges, as well as some combat encounters and social encounters.",
    features=[
        "coast",
        "water",
    ],
    tiers=[Tiers.tier_1, Tiers.tier_2, Tiers.tier_3],
    weather=[
        "clear",
        "overcast",
        "rain",
        "mist",
    ],
    biomes={Biome.ocean, Biome.lake},
    terrains={Terrain.water},
    development={Development.wilderness},  # Not specific to development
)

RollingGrasslands = Region(
    name="Rolling Grasslands",
    description="There is great prosperity among the people that call these fields and rolling hills home. Adventurers journeying through this region have frequent social encounters, few combat encounters, and several circumstance exploration challenges.",
    features=[
        "grassland",
        "hills",
        "ruins",
        "settlement",
        "subterranean",
        "temple",
        "tomb",
    ],
    tiers=[Tiers.tier_1, Tiers.tier_2],
    weather=[
        "clear",
        "overcast",
        "rain",
        "mist",
        "snow",
    ],
    biomes={Biome.grassland, Biome.farmland},
    terrains={Terrain.hill, Terrain.plain},
    development={
        Development.settlement,
        Development.frontier,
        Development.wilderness,
        Development.countryside,
    },
)

TangledForest = Region(
    name="Tangled Forest",
    description="From temperate forests and woodlands which harbor bandit encampments to lush tropical jungles home to giant apes and mighty dinosaurs, these regions are covered with trees and undergrowth. Adventurers journeying through regions like this contend with frequent monster encounters and natural terrain and supernatural exploration challenges.",
    features=[
        "forest",
        "jungle",
        "mountains",
        "ruins",
        "settlement",
        "subterranean",
        "swamp",
        "temple",
        "tomb",
    ],
    tiers=[Tiers.tier_1, Tiers.tier_2, Tiers.tier_3, Tiers.tier_4],
    weather=[
        "clear",
        "mist",
        "rain",
        "snow",
    ],
    biomes={Biome.forest, Biome.jungle, Biome.swamp, Biome.underground},
    terrains={Terrain.hill, Terrain.mountain, Terrain.plain},
    development={Development.wilderness, Development.frontier, Development.ruin},
)

UnderlandRealm = Region(
    name="Underland Realm",
    description="There is no map—even among the subterranean cultures that dwell within—that accurately depicts all of these enormous tunnels, which range from natural caverns and dwarven mines to shadow elf cities. Adventurers journeying through this region have combat encounters, some social encounters, and many constructed terrain, natural terrain, and supernatural exploration challenges.",
    features=[
        "forest",
        "jungle",
        "laboratory",
        "ruins",
        "settlement",
        "subterranean",
        "swamp",
        "temple",
        "tomb",
        "water",
    ],
    tiers=[Tiers.tier_2, Tiers.tier_3, Tiers.tier_4],
    weather=[
        "clear",
        "mist",
    ],
    biomes={Biome.underground},
    terrains={Terrain.hill, Terrain.plain},
    development={
        Development.ruin,
        Development.settlement,
        Development.frontier,
        Development.wilderness,
    },
)

UnrelentingMarsh = Region(
    name="Unrelenting Marsh",
    description="So named because time seems to slow to a crawl while traversing its swamps, this area is rife with dangerous predators, lethal fauna, and ground best left untrusted. Adventurers journeying through this region have frequent combat encounters, a few social encounters, and many natural terrain exploration challenges.",
    features=[
        "forest",
        "grassland",
        "hills",
        "jungle",
        "ruins",
        "settlement",
        "swamp",
        "temple",
        "tomb",
        "water",
    ],
    tiers=[Tiers.tier_1, Tiers.tier_2, Tiers.tier_3, Tiers.tier_4],
    weather=[
        "clear",
        "overcast",
        "rain",
        "mist",
    ],
    biomes={Biome.swamp, Biome.forest, Biome.jungle, Biome.lake},
    terrains={Terrain.hill, Terrain.plain},
    development={
        Development.ruin,
        Development.settlement,
        Development.frontier,
        Development.wilderness,
    },
)

UrbanTownship = Region(
    name="Urban Township",
    description="From mighty sprawling cities to smaller bustling towns, these areas are full of people—and more people means more accidents, more conflict, and more action. Adventurers journeying through urban areas have many social encounters, combat encounters against NPCs, and both circumstance and constructed terrain exploration challenges.",
    features=[
        "settlement",
        "sewer",
        "temple",
    ],
    tiers=[Tiers.tier_1, Tiers.tier_2, Tiers.tier_3, Tiers.tier_4],
    weather=[
        "clear",
        "overcast",
        "rain",
        "mist",
        "snow",
    ],
    development={Development.settlement, Development.urban},
)

WartornKingdom = Region(
    name="Wartorn Kingdom",
    description="An occupied nation, or one amidst a civil war, is a dubious place populated with aggressive soldiers, desperate commoners, and merciless opportunists. Adventurers journeying through this region have many social encounters, combat encounters against NPCs, and both circumstance and natural terrain exploration challenges as they navigate the country in conflict.",
    features=["any"],
    tiers=[Tiers.tier_1, Tiers.tier_2, Tiers.tier_3],
    weather=[
        "clear",
        "overcast",
        "rain",
        "mist",
        "snow",
    ],
    biomes=None,  # Any biome
    terrains=None,  # Any terrain
    development={
        Development.ruin,
        Development.countryside,
        Development.frontier,
        Development.urban,
    },
)

AllRegions = [
    BlastedBadlands,
    CountryShire,
    Feywood,
    FieryHellscape,
    FlowingRiver,
    FrozenWastes,
    HauntedLands,
    LoftyMountains,
    OpenRoads,
    ParchedSands,
    RestlessSea,
    RollingGrasslands,
    TangledForest,
    UnderlandRealm,
    UnrelentingMarsh,
    UrbanTownship,
    WartornKingdom,
]

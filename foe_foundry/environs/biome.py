from enum import StrEnum, auto


class Biome(StrEnum):
    """Types of biomes that can be found in the environment. Biomes represent the natural characteristics of a region, including its climate, vegetation, and wildlife."""

    arctic = auto()  # cold, icy regions with snow and glaciers.
    desert = auto()  # hot, dry regions with sand and little vegetation.
    forest = auto()  # wooded areas with trees, shrubs, and diverse wildlife.
    jungle = auto()  # dense, tropical forests with high humidity and rich biodiversity.
    grassland = (
        auto()
    )  # open, grassy areas with few trees, often home to grazing animals.
    farmland = auto()  # cultivated land used for agriculture, with crops and livestock.
    ocean = auto()  # vast bodies of saltwater, home to marine life.
    river = (
        auto()
    )  # flowing bodies of freshwater, often with banks and surrounding ecosystems.
    lake = (
        auto()
    )  # large bodies of freshwater, often surrounded by land and ecosystems.
    swamp = auto()  # wetland areas with slow-moving water, often rich in biodiversity.
    underground = auto()  # subterranean environments, such as caves and tunnels.
    extraplanar = auto()  # environments that exist outside the material plane.

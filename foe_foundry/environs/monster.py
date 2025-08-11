from typing import TypeAlias

from .affinity import Affinity
from .biome import Biome
from .development import Development
from .extraplanar import ExtraplanarInfluence
from .region import Region
from .terrain import Terrain

"""Type aliases for monster environmental affinity

    Affinity can be expressed in terms of a:
      - Region: An area of the world with specific biomes, terrains, development, or extraplanar influence. This is a higher-level way of expressing environments compared to the other options
      - Biome:  Biomes represent the natural characteristics of a region, including its climate, vegetation, and wildlife.
      - Terrain: Terrain refers to the physical features of the land, including its shape, elevation, and surface materials.
      - Development: Levels of development in the environment caused by sentient creatures and civilization, former or present.
      - ExtraplanarInfluence: The impact of extraplanar entities or forces on the environment, often resulting in unique or altered conditions.
"""
EnvironmentAffinity: TypeAlias = tuple[
    Region | Biome | Development | Terrain | ExtraplanarInfluence, Affinity
]

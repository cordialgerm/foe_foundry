from enum import StrEnum, auto


class Terrain(StrEnum):
    """Types of terrain that can be found in the environment. Terrain refers to the physical features of the land, including its shape, elevation, and surface materials."""

    mountain = auto()  # high, rocky areas with steep slopes and peaks.
    hill = auto()  # elevated landforms, often with gentle slopes.
    plain = auto()  # flat, open areas with few obstacles.
    water = auto()  # areas covered by water, such as lakes, rivers, and oceans.

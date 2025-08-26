from enum import auto

try:
    from enum import StrEnum  # Python 3.11+
except ImportError:
    from backports.strenum import StrEnum  # Python 3.10


class Development(StrEnum):
    """Levels of development in the environment caused by sentient creatures and civilization, former or present."""

    wilderness = auto()  # no development. Natural wilderness and terrain.
    frontier = auto()  # minimal development. Small settlements, farms, and outposts.
    countryside = auto()  # within the sphere of civilization, but not fully developed. Villages, towns, and some infrastructure.
    settlement = auto()  # established communities with basic infrastructure.
    urban = (
        auto()
    )  # significant development. Cities, roads, and advanced infrastructure.
    ruin = (
        auto()
    )  # abandoned or destroyed areas, often overgrown or reclaimed by nature.
    stronghold = auto()  # fortified areas, often military or strategic in nature.
    dungeon = auto()  # underground or hidden areas, often with traps and treasures.

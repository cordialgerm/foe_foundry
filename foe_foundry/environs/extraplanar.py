from enum import auto

try:
    from enum import StrEnum  # Python 3.11+
except ImportError:
    from backports.strenum import StrEnum  # Python 3.10


class ExtraplanarInfluence(StrEnum):
    none = auto()  # no extraplanar influence. The material plane itself.
    astral = (
        auto()
    )  # influence from the astral plane. Ethereal and dreamlike qualities.
    elemental = (
        auto()
    )  # influence from elemental planes. Strong elemental characteristics.
    faerie = auto()  # influence from the faerie realm. Magical and whimsical qualities.
    celestial = (
        auto()
    )  # influence from celestial planes. Divine and holy characteristics.
    hellish = (
        auto()
    )  # influence from hellish planes. Dark and infernal characteristics.
    deathly = auto()  # influence from the realm of death. Dark and eerie qualities.

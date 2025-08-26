from __future__ import annotations

from enum import auto

try:
    from enum import StrEnum  # Python 3.11+
except ImportError:
    from backports.strenum import StrEnum  # Python 3.10


class PowerCategory(StrEnum):
    Role = auto()  # powers that are tied to a specific role
    CreatureType = auto()  # powers that are tied to a specific creature type
    Creature = auto()  # powers that are tied to a specific creature template
    Theme = auto()  # powers that are related to a common theme
    Spellcasting = auto()  # powers that are tied to a specific spellcasting theme
    Species = auto()  # powers that are tied to a specific species

    @staticmethod
    def All() -> list[PowerCategory]:
        return [
            PowerCategory.Role,
            PowerCategory.CreatureType,
            PowerCategory.Creature,
            PowerCategory.Theme,
            PowerCategory.Spellcasting,
            PowerCategory.Species,
        ]

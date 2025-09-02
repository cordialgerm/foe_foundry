from __future__ import annotations

from enum import StrEnum, auto


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

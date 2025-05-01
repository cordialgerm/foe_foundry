from __future__ import annotations

from enum import auto

from backports.strenum import StrEnum


class PowerType(StrEnum):
    Role = auto()  # powers that are tied to a specific role
    CreatureType = auto()  # powers that are tied to a specific creature type
    Creature = auto()  # powers that are tied to a specific creature template
    Theme = auto()  # powers that are related to a common theme
    Spellcasting = auto()  # powers that are tied to a specific spellcasting theme
    Species = auto()  # powers that are tied to a specific species

    @staticmethod
    def All() -> list[PowerType]:
        return [
            PowerType.Role,
            PowerType.CreatureType,
            PowerType.Creature,
            PowerType.Theme,
            PowerType.Spellcasting,
            PowerType.Species,
        ]

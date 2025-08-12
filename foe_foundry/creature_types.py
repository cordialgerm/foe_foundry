from __future__ import annotations

from enum import auto
from typing import Set

from backports.strenum import StrEnum


class CreatureType(StrEnum):
    Aberration = auto()
    Beast = auto()
    Celestial = auto()
    Construct = auto()
    Dragon = auto()
    Elemental = auto()
    Fey = auto()
    Fiend = auto()
    Giant = auto()
    Humanoid = auto()
    Monstrosity = auto()
    Ooze = auto()
    Plant = auto()
    Undead = auto()

    @staticmethod
    def parse(creature_type: str) -> CreatureType:
        try:
            return CreatureType[creature_type.title()]
        except KeyError:
            raise ValueError(f"Unknown creature type: {creature_type}")

    @property
    def is_living(self) -> bool:
        return self in {
            CreatureType.Aberration,
            CreatureType.Beast,
            CreatureType.Dragon,
            CreatureType.Fey,
            CreatureType.Giant,
            CreatureType.Humanoid,
            CreatureType.Monstrosity,
            CreatureType.Ooze,
            CreatureType.Plant,
        }

    @property
    def could_use_weapon(self) -> bool:
        return self in {
            CreatureType.Celestial,
            CreatureType.Fiend,
            CreatureType.Fey,
            CreatureType.Humanoid,
            CreatureType.Construct,
            CreatureType.Giant,
        }

    @property
    def could_wear_armor(self) -> bool:
        return self.could_wear_light_armor or self.could_wear_heavy_armor

    @property
    def could_wear_heavy_armor(self) -> bool:
        return self in {
            CreatureType.Celestial,
            CreatureType.Fiend,
            CreatureType.Fey,
            CreatureType.Humanoid,
            CreatureType.Construct,
            CreatureType.Giant,
            CreatureType.Undead,
            CreatureType.Elemental,
        }

    @property
    def could_wear_light_armor(self) -> bool:
        return self in {
            CreatureType.Celestial,
            CreatureType.Fey,
            CreatureType.Humanoid,
            CreatureType.Giant,
            CreatureType.Undead,
        }

    @property
    def could_use_equipment(self) -> bool:
        return self in {
            CreatureType.Fey,
            CreatureType.Humanoid,
            CreatureType.Construct,
            CreatureType.Giant,
        }

    @property
    def could_be_organized(self) -> bool:
        return self in {
            CreatureType.Humanoid,
            CreatureType.Fey,
            CreatureType.Dragon,
            CreatureType.Giant,
        }

    @staticmethod
    def all():
        return CreatureType.all_but()

    @staticmethod
    def all_but(*creature_type: CreatureType) -> Set[CreatureType]:
        exclusions = set(creature_type)
        all = {c for c in CreatureType}
        return all - exclusions

    @staticmethod
    def parse(ct: str) -> CreatureType:
        return CreatureType(ct.lower())

from abc import ABC, abstractmethod
from dataclasses import field
from typing import Any

from pydantic.dataclasses import dataclass


@dataclass
class ResolvedArmorClass:
    value: int
    armor_type: str
    has_shield: bool
    is_armored: bool
    display_detail: bool
    quality_level: int
    score: float
    description: str = field(init=False)

    def __post_init__(self):
        if not self.display_detail:
            self.description = str(self.value)
        elif self.has_shield:
            self.description = f"{self.value} ({self.armor_type}, Shield)"
        else:
            self.description = f"{self.value} ({self.armor_type})"

    def __repr__(self) -> str:
        return self.description


class ArmorClassTemplate(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def is_armored(self) -> bool:
        raise NotImplementedError

    @property
    @abstractmethod
    def is_heavily_armored(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def resolve(self, stats: Any, uses_shield: bool) -> ResolvedArmorClass:
        raise NotImplementedError

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ArmorClassTemplate):
            return NotImplemented

        return (
            self.name == other.name
            and self.is_armored == other.is_armored
            and self.is_heavily_armored == other.is_heavily_armored
        )

    def __hash__(self) -> int:
        return hash(self.name)

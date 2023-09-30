from abc import ABC, abstractmethod, abstractproperty
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ResolvedArmorClass:
    value: int
    armor_type: str
    has_shield: bool
    is_armored: bool
    quality_level: int
    score: float
    description: str = field(init=False)

    def __post_init__(self):
        self.description = f"{self.value} ({self.armor_type})"

    def __repr__(self) -> str:
        return self.description


class ArmorClassTemplate(ABC):
    @abstractproperty
    def name(self) -> str:
        raise NotImplementedError

    @abstractproperty
    def can_use_shield(self) -> bool:
        raise NotImplementedError

    @abstractproperty
    def is_armored(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def resolve(self, stats: Any, uses_shield: bool) -> ResolvedArmorClass:
        raise NotImplementedError

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Tuple

from ..features import Feature
from ..statblocks import BaseStatblock
from .rarity import PowerRarity


class Power(ABC):
    def __init__(self, name: str, rarity: PowerRarity):
        self.name = name
        self.rarity = rarity

    @property
    def key(self) -> str:
        return self.name.lower().replace(" ", "_")

    @abstractmethod
    def score(self, candidate: BaseStatblock) -> float:
        pass

    @abstractmethod
    def apply(self, stats: BaseStatblock) -> Tuple[BaseStatblock, Feature]:
        pass

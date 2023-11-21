from abc import ABC, abstractmethod
from typing import List, Tuple

import numpy as np

from ..creature_types import CreatureType
from ..damage import DamageType
from ..features import Feature
from ..role_types import MonsterRole
from ..statblocks import BaseStatblock
from .power_type import PowerType

LOW_POWER = 0.5
MEDIUM_POWER = 1
HIGH_POWER = 1.5


class Power(ABC):
    def __init__(
        self,
        name: str,
        power_type: PowerType,
        source: str | None = None,
        power_level: float = MEDIUM_POWER,
        roles: List[MonsterRole] | None = None,
        creature_types: List[CreatureType] | None = None,
        damage_types: List[DamageType] | None = None,
    ):
        self.name = name
        self.power_type = power_type
        self.source = source
        self.power_level = power_level
        self.roles = roles
        self.creature_types = creature_types
        self.damage_types = damage_types

        if self.power_level == HIGH_POWER:
            self.power_level_text = "High Power"
        elif self.power_level == MEDIUM_POWER:
            self.power_level_text = "Medium Power"
        elif self.power_level == LOW_POWER:
            self.power_level_text = "Low Power"
        else:
            raise ValueError(f"Invalid power level {self.power_level}")

    @property
    def key(self) -> str:
        return Power.name_to_key(self.name)

    @abstractmethod
    def score(self, candidate: BaseStatblock) -> float:
        pass

    def modify_stats(self, stats: BaseStatblock) -> BaseStatblock:
        return stats

    @abstractmethod
    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        pass

    def __repr__(self):
        return f"{self.name} ({self.power_type})"

    def __hash__(self) -> int:
        return hash(type(self))

    @staticmethod
    def name_to_key(name: str) -> str:
        return name.lower().replace(" ", "-")


class PowerBackport(Power):
    def __init__(
        self,
        name: str,
        power_type: PowerType,
        source: str | None = None,
        power_level: float = MEDIUM_POWER,
    ):
        super().__init__(
            name=name, power_type=power_type, source=source, power_level=power_level
        )

    def modify_stats(self, stats: BaseStatblock) -> BaseStatblock:
        new_stats, _ = self.apply(stats, np.random.default_rng(20210518))
        return new_stats

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        _, features = self.apply(stats, np.random.default_rng(20210518))
        return Feature.merge(features)

    @abstractmethod
    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature | List[Feature] | None]:
        pass

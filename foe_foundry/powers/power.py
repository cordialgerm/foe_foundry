from abc import ABC, abstractmethod
from typing import Tuple

import numpy as np

from ..features import Feature
from ..statblocks import BaseStatblock
from .power_type import PowerType


class Power(ABC):
    def __init__(self, name: str, power_type: PowerType):
        self.name = name
        self.power_type = power_type
        self.rng = np.random.default_rng(20210518)

    @property
    def key(self) -> str:
        return self.name.lower().replace(" ", "_")

    @abstractmethod
    def score(self, candidate: BaseStatblock) -> float:
        pass

    @abstractmethod
    def apply(self, stats: BaseStatblock) -> Tuple[BaseStatblock, Feature]:
        pass

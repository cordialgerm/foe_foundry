from abc import ABC, abstractmethod

import numpy as np

from ..creature_types import CreatureType
from ..statblocks import BaseStatblock


class CreatureTypeTemplate(ABC):
    def __init__(self, name: str, creature_type: CreatureType):
        self.name = name
        self.creature_type = creature_type
        self.rng = np.random.default_rng(20210518)

    @property
    def key(self) -> str:
        return self.name.lower().replace(" ", "_")

    @abstractmethod
    def apply(self, stats: BaseStatblock) -> BaseStatblock:
        pass

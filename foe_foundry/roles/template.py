from abc import ABC, abstractmethod
from typing import Callable, List

import numpy as np

from foe_foundry.statblocks import BaseStatblock

from ..role_types import MonsterRole
from ..statblocks import BaseStatblock


class RoleVariant(ABC):
    def __init__(self, name: str, role: MonsterRole):
        self.name = name
        self.role = role

    @property
    def key(self) -> str:
        return self.name.lower().replace(" ", "_").replace(".", "_")

    @abstractmethod
    def alter_base_stats(self, stats: BaseStatblock) -> BaseStatblock:
        pass


class RoleTemplate:
    def __init__(self, name: str, role: MonsterRole, variants: List[RoleVariant]):
        self.name = name
        self.role = role
        self.counter = 0
        self.variants = variants

    @property
    def key(self) -> str:
        return self.name.lower().replace(" ", "_")

    def alter_base_stats(self, stats: BaseStatblock, rng: np.random.Generator):
        if len(self.variants) == 1:
            i = 0
        else:
            i = rng.choice(len(self.variants))
        v = self.variants[i]
        return v.alter_base_stats(stats=stats)

    def alter_base_stats_cycle(self, stats: BaseStatblock) -> BaseStatblock:
        try:
            v = self.variants[self.counter % len(self.variants)]
            return v.alter_base_stats(stats=stats)
        finally:
            self.counter += 1


class RoleVariantWrapper(RoleVariant):
    def __init__(self, name: str, role: MonsterRole, callback: Callable):
        super().__init__(name=name, role=role)
        self.callback = callback

    def alter_base_stats(self, *args, **kwargs) -> BaseStatblock:
        return self.callback(*args, **kwargs)


def role_variant(name: str, role: MonsterRole, apply: Callable) -> RoleVariant:
    return RoleVariantWrapper(name=name, role=role, callback=apply)

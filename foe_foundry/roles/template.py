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
    def apply(self, stats: BaseStatblock) -> BaseStatblock:
        pass


class RoleTemplate:
    def __init__(self, name: str, role: MonsterRole, variants: List[RoleVariant]):
        self.name = name
        self.role = role
        self.rng = np.random.default_rng(20210518)
        self.counter = 0
        self.variants = variants

    @property
    def key(self) -> str:
        return self.name.lower().replace(" ", "_")

    def apply(self, stats: BaseStatblock) -> BaseStatblock:
        try:
            v = self.variants[self.counter % len(self.variants)]
            return v.apply(stats=stats)
        finally:
            self.counter += 1


class RoleVariantWrapper(RoleVariant):
    def __init__(self, name: str, role: MonsterRole, callback: Callable):
        super().__init__(name=name, role=role)
        self.callback = callback

    def apply(self, *args, **kwargs) -> BaseStatblock:
        return self.callback(*args, **kwargs)


def role_variant(name: str, role: MonsterRole, apply: Callable) -> RoleVariant:
    return RoleVariantWrapper(name=name, role=role, callback=apply)

from abc import ABC, abstractmethod

from ..role_types import MonsterRole
from ..statblocks import BaseStatblock


class RoleTemplate(ABC):
    def __init__(self, name: str, role: MonsterRole):
        self.name = name
        self.role = role

    @property
    def key(self) -> str:
        return self.name.lower().replace(" ", "_")

    @abstractmethod
    def alter_base_stats(self, stats: BaseStatblock) -> BaseStatblock:
        pass

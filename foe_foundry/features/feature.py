from __future__ import annotations

from dataclasses import field, replace
from typing import List

from pydantic.dataclasses import dataclass

from .action_type import ActionType


@dataclass
class Feature:
    name: str
    description: str
    action: ActionType
    recharge: int | None = None
    uses: int | None = None
    replaces_multiattack: int = 0
    special_condition: str | None = None
    hidden: bool = False
    modifies_attack: bool = False
    creates_token: bool = False
    title: str = field(init=False)

    def __post_init__(self):
        if self.special_condition is not None:
            self.title = f"{self.name} ({self.special_condition})"
        elif self.recharge is not None:
            if self.recharge == 6:
                self.title = f"{self.name} (Recharge {self.recharge})"
            else:
                self.title = f"{self.name} (Recharge {self.recharge}-6)"
        elif self.uses is not None:
            self.title = f"{self.name} ({self.uses}/day)"
        else:
            self.title = self.name

    def copy(self, **kwargs) -> Feature:
        return replace(self, **kwargs)

    def __hash__(self) -> int:
        return self.name.__hash__()

    @staticmethod
    def merge(*features: Feature | List[Feature] | None) -> List[Feature]:
        results = []

        for item in features:
            if isinstance(item, Feature):
                results.append(item)
            elif isinstance(item, list):
                results.extend(item)

        return results

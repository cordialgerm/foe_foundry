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
    power_key: str | None = None
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

    @property
    def recharge_priority(self) -> float:
        if self.recharge is None:
            return 0.0

        # abilities with a high recharge are more powerful, so they should have higher priority
        if self.recharge == 6:
            priority = 1.5
        elif self.recharge == 5:
            priority = 1.0
        else:
            priority = 0.75

        # active abilities like actions and bonus actions should take precedence over passive abilities
        if self.action == ActionType.Action:
            priority *= 1.25
        elif self.action == ActionType.BonusAction:
            priority *= 1.0
        else:
            priority *= 0.75

        # abilities that create tokens are unique and should be prioritized
        if self.creates_token:
            priority *= 1.25

        # abilities that replace multiattacks are intended to be useed often, so a recharge makes sense
        if self.replaces_multiattack >= 2:
            priority *= 1.5
        elif self.replaces_multiattack == 1:
            priority *= 1.25

        # abilities with longer descriptions are more complex and probably more powerful because of that
        length_multiplier = 1.0 + (len(self.description) / 500.0)
        priority *= length_multiplier

        return priority

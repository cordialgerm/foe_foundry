from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ArmorClass:
    value: int
    description: str | None = None

    def delta(self, val: int) -> ArmorClass:
        return ArmorClass(value=self.value + val, description=self.description)

from __future__ import annotations

from typing import List, cast

try:
    from enum import StrEnum  # Python 3.11+
except ImportError:
    from backports.strenum import StrEnum  # Python 3.10


class Die(StrEnum):
    d4 = "d4"
    d6 = "d6"
    d8 = "d8"
    d10 = "d10"
    d12 = "d12"
    d20 = "d20"

    @staticmethod
    def All() -> List[Die]:
        return [cast(Die, s) for s in Die._member_map_.values()]

    @staticmethod
    def parse(die: str) -> Die:
        val = Die.__dict__.get(die.strip().lower())
        if val is None:
            raise ValueError(f"Unsupported value: {die}")
        return val

    def as_numeric(self) -> int:
        return int(self.name[1:])

    def __ge__(self, other: Die) -> bool:
        return self.as_numeric() >= other.as_numeric()

    def __gt__(self, other: Die) -> bool:
        return self.as_numeric() > other.as_numeric()

    def __lt__(self, other: Die) -> bool:
        return self.as_numeric() < other.as_numeric()

    def __lte__(self, other: Die) -> bool:
        return self.as_numeric() <= other.as_numeric()

    def average(self) -> float:
        return (1 + self.as_numeric()) / 2

    def increase(self) -> Die:
        dies = Die.All()
        mapping = {d: i for i, d in enumerate(dies)}
        i = mapping[self]
        if i == len(mapping) - 1:
            return self
        else:
            return dies[i + 1]

    def decrease(self) -> Die:
        dies = Die.All()
        mapping = {d: i for i, d in enumerate(dies)}
        i = mapping[self]
        if i == 0:
            return self
        else:
            return dies[i - 1]

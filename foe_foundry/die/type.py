from __future__ import annotations
from enum import StrEnum
from typing import List, cast


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

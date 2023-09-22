from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import cast


@dataclass
class Movement:
    walk: int
    fly: int | None = None
    climb: int | None = None
    swim: int | None = None
    burrow: int | None = None
    hover: bool = False

    @property
    def fastest_speed(self) -> int:
        return max(self.walk, self.fly or 0, self.climb or 0, self.swim or 0, self.burrow or 0)

    def delta(self, speed_change: int) -> Movement:
        args = {}
        for k, v in asdict(self).items():
            if v is not None and (m := cast(int, v)) > 0:
                args[k] = m + speed_change
        return Movement(**args)

    def copy(self, **kwargs) -> Movement:
        args = asdict(self)
        args.update(kwargs)
        return Movement(**args)

    def grant_flying(self) -> Movement:
        if self.fly:
            return self.copy()
        else:
            return self.copy(fly=self.walk)

    def grant_climbing(self) -> Movement:
        if self.climb:
            return self.copy()
        else:
            return self.copy(climb=self.walk)

    def grant_swim(self) -> Movement:
        if self.swim:
            return self.copy()
        else:
            return self.copy(swim=self.walk)

    def describe(self) -> str:
        pieces = [f"{self.walk} ft."]

        def add(type: str, v: int | None, postfix: str | None = None):
            if v is not None:
                postfix = f"({postfix})" if postfix is not None else ""
                pieces.append(f"{type} {v} ft.{postfix}")

        add("climb", self.climb)
        add("fly", self.fly, "hover" if self.hover else None)
        add("swim", self.swim)

        return ", ".join(pieces)

    def __repr__(self) -> str:
        return self.describe()

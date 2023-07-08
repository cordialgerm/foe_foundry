from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import cast


@dataclass
class Movement:
    walk: int
    fly: int | None = None
    climb: int | None = None
    swim: int | None = None
    hover: bool = False

    def delta(self, speed_change: int) -> Movement:
        args = {}
        for k, v in asdict(self).items():
            if v is not None and (m := cast(int, v)) > 0:
                args[k] = m + speed_change
        return Movement(**args)

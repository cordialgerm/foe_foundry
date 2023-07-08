from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass
class Senses:
    darkvision: int = 0
    blindsight: int = 0
    truesight: int = 0

    def copy(self, **args) -> Senses:
        kwargs = asdict(self)
        kwargs.update(args)
        return Senses(**kwargs)

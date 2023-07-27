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

    def describe(self, passive_perception: int) -> str:
        pieces = []

        def add(type: str, v: int | None):
            if v is not None and v > 0:
                pieces.append(f"{type} {v} ft.")

        add("Blindsight", self.blindsight)
        add("Darkvision", self.darkvision)
        add("Truesight", self.truesight)
        pieces.append(f"Passive Perception {passive_perception}")

        return ", ".join(pieces)

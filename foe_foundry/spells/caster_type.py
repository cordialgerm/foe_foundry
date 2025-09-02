from __future__ import annotations

from enum import StrEnum
from typing import Set


class CasterType(StrEnum):
    Arcane = "Arcane"
    Primal = "Primal"
    Divine = "Divine"
    Psionic = "Psionic"
    Pact = "Pact"
    Innate = "Innate"

    @staticmethod
    def all() -> Set[CasterType]:
        all = {c for c in CasterType}
        return all

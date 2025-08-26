from __future__ import annotations

from typing import Set

try:
    from enum import StrEnum  # Python 3.11+
except ImportError:
    from backports.strenum import StrEnum  # Python 3.10


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

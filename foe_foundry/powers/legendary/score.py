from dataclasses import dataclass

try:
    from enum import StrEnum  # Python 3.11+
except ImportError:
    from backports.strenum import StrEnum  # Python 3.10

from ...features import Feature


class LegendaryActionType(StrEnum):
    move = "move"
    attack = "attack"
    special = "special"


@dataclass
class LegendaryActionScore:
    feature: Feature
    types: set[LegendaryActionType]
    score: float

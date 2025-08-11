from dataclasses import dataclass

from backports.strenum import StrEnum

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

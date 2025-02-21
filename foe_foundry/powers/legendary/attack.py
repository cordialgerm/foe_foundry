from typing import Iterable

from ...features import ActionType, Feature
from ...statblocks import BaseStatblock
from .score import LegendaryActionScore, LegendaryActionType


def attack(stats: BaseStatblock) -> Iterable[LegendaryActionScore]:
    attacks = [stats.attack]
    attacks += [
        a for a in stats.additional_attacks if a.is_equivalent_to_primary_attack
    ]
    attack_names = " or ".join(a.display_name for a in attacks)

    yield LegendaryActionScore(
        feature=Feature(
            name="Attack",
            description=f"{stats.selfref.title()} makes a {attack_names} attack.",
            action=ActionType.Legendary,
        ),
        types={LegendaryActionType.attack},
        score=0,
    )

import numpy as np

from ...features import Feature
from ...statblocks import BaseStatblock
from .attack import attack
from .move import move
from .score import LegendaryActionScore, LegendaryActionType
from .special import special


def _take(
    type: LegendaryActionType, scores: list[LegendaryActionScore], n: int = 1
) -> list[LegendaryActionScore]:
    options = np.array([s for s in scores if type in s.types], dtype=object)
    if len(options) == 0:
        return []
    option_scores = np.array([s.score for s in options])
    indexes = np.argsort(option_scores)[::-1]
    return options[indexes[0:n]].tolist()  # type: ignore


def _resolve(
    scores: list[LegendaryActionScore],
) -> list[LegendaryActionScore]:
    t1 = _take(LegendaryActionType.attack, scores, n=1)

    if len(t1) and LegendaryActionType.move in t1[0].types:
        t2 = []
    else:
        t2 = _take(LegendaryActionType.move, scores, n=1)

    t3 = _take(LegendaryActionType.special, scores, n=3 - len(t1) - len(t2))
    return t1 + t2 + t3


def get_legendary_actions(
    stats: BaseStatblock, features: list[Feature]
) -> list[Feature]:
    options = []
    for a in attack(stats):
        options.append(a)
    for a in move(stats):
        options.append(a)
    for a in special(stats, features):
        options.append(a)

    actions = _resolve(options)
    return [a.feature for a in actions]

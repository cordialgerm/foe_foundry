from __future__ import annotations

from enum import StrEnum, auto
from typing import List

import numpy as np


class Size(StrEnum):
    Tiny = auto()
    Small = auto()
    Medium = auto()
    Large = auto()
    Huge = auto()
    Gargantuan = auto()

    @staticmethod
    def All() -> List[Size]:
        return [Size.Tiny, Size.Small, Size.Medium, Size.Large, Size.Huge, Size.Gargantuan]


def get_size_for_cr(cr: float, standard_size: Size, rng: np.random.Generator):
    size_lookup = {s: i for i, s in enumerate(Size.All())}
    p = size_lookup[standard_size]

    weights = np.array([1, 5, 10, 1, 1, 1])
    indxs = np.arange(len(weights))

    if p == 0:
        weights[0] += 20
        weights[1] += 10
    elif p == len(weights):
        weights[-1] += 20
        weights[-2] += 10
    else:
        weights[p] += 20
        weights[p - 1] += 10
        weights[p + 1] += 10

    if cr <= 1:
        weights[indxs >= 3] = 0
    elif cr <= 5:
        weights[[0, 5]] = 0
    elif cr <= 10:
        weights[[0, 5]] = 0
    else:
        weights[indxs < 3] = 0

    weights = np.array(weights) / np.sum(weights)
    size_indx = rng.choice(len(Size.All()), p=weights)
    return Size.All()[size_indx]

from __future__ import annotations

from enum import StrEnum, auto
from typing import Dict, List

import numpy as np

from .die import Die


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

    @staticmethod
    def Ordinals() -> Dict[Size, int]:
        return {s: i for i, s in enumerate(Size.All())}

    def __le__(self, other: Size) -> bool:
        o = Size.Ordinals()
        a = o[self]
        b = o[other]
        return a <= b

    def __lt__(self, other: Size) -> bool:
        o = Size.Ordinals()
        a = o[self]
        b = o[other]
        return a < b

    def __gt__(self, other: Size) -> bool:
        o = Size.Ordinals()
        a = o[self]
        b = o[other]
        return a > b

    def __ge__(self, other: Size) -> bool:
        o = Size.Ordinals()
        a = o[self]
        b = o[other]
        return a >= b

    def __sub__(self, other: Size) -> int:
        ordinals = Size.Ordinals()
        o1 = ordinals[self]
        o2 = ordinals[other]
        return o1 - o2

    def increment(self) -> Size:
        if self == Size.Tiny:
            return Size.Small
        elif self == Size.Small:
            return Size.Medium
        elif self == Size.Medium:
            return Size.Large
        elif self == Size.Large:
            return Size.Huge
        elif self == Size.Huge:
            return Size.Gargantuan
        elif self == Size.Gargantuan:
            return Size.Gargantuan
        else:
            raise ValueError("Shouldn't happen")

    def decrement(self) -> Size:
        if self == Size.Tiny:
            return Size.Tiny
        elif self == Size.Small:
            return Size.Tiny
        elif self == Size.Medium:
            return Size.Small
        elif self == Size.Large:
            return Size.Medium
        elif self == Size.Huge:
            return Size.Large
        elif self == Size.Gargantuan:
            return Size.Huge
        else:
            raise ValueError("Shouldn't happen")

    def hit_die(self) -> Die:
        if self == Size.Tiny:
            return Die.d4
        elif self == Size.Small:
            return Die.d6
        elif self == Size.Medium:
            return Die.d8
        elif self == Size.Large:
            return Die.d10
        elif self == Size.Huge:
            return Die.d12
        else:
            return Die.d20


def get_size_for_cr(cr: float, standard_size: Size, rng: np.random.Generator):
    if cr <= 1:
        weights = [0.3, 0.6, 0.1]
    elif cr <= 5:
        weights = [0.05, 0.7, 0.25]
    elif cr <= 10:
        weights = [0, 0.4, 0.6]
    else:
        weights = [0, 0.2, 0.8]

    i = rng.choice(3, p=weights)

    if i == 0:
        return standard_size.decrement()
    elif i == 1:
        return standard_size
    else:
        return standard_size.increment()

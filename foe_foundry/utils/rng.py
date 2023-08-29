from enum import StrEnum
from typing import List, TypeVar, overload

import numpy as np

T = TypeVar("T", bound=StrEnum)


@overload
def choose_enum(rng: np.random.Generator, values: List[T]) -> T:
    pass


@overload
def choose_enum(rng: np.random.Generator, values: List[T], size: int) -> List[T]:
    pass


def choose_enum(
    rng: np.random.Generator, values: List[T], size: int | None = None, **args
) -> T | List[T]:
    indxs = rng.choice(a=len(values), size=size, **args)
    if isinstance(indxs, int):
        return values[indxs]
    else:
        return [values[i] for i in indxs]

from enum import StrEnum
from typing import List, TypeVar, overload

import numpy as np

T = TypeVar("T", bound=StrEnum)


@overload
def choose_enum(rng: np.random.Generator, values: List[T]) -> T:
    pass


@overload
def choose_enum(
    rng: np.random.Generator, values: List[T], size: int, replace: bool = False
) -> List[T]:
    pass


def choose_enum(
    rng: np.random.Generator,
    values: List[T],
    size: int | None = None,
    replace: bool = False,
    **args
) -> T | List[T]:
    indxs = rng.choice(a=len(values), size=size, replace=replace, **args)
    if isinstance(indxs, int):
        return values[indxs]
    else:
        return [values[i] for i in indxs]

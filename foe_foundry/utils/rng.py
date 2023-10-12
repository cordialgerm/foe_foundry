from enum import StrEnum
from typing import Any, List, TypeVar, overload

import numpy as np

T = TypeVar("T", bound=StrEnum)


@overload
def choose_enum(rng: np.random.Generator, values: List[T], p: Any = None) -> T:
    pass


@overload
def choose_enum(
    rng: np.random.Generator,
    values: List[T],
    p: Any = None,
    size: int | None = None,
    replace: bool = False,
) -> List[T]:
    pass


def choose_enum(
    rng: np.random.Generator,
    values: List[T],
    p: Any = None,
    size: int | None = None,
    replace: bool = False,
) -> T | List[T]:
    if p is not None:
        p = np.array(p) / np.sum(p)

    indxs = rng.choice(a=len(values), size=size, replace=replace, p=p)
    if isinstance(indxs, int):
        return values[indxs]
    else:
        return [values[i] for i in indxs]

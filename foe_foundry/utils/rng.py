from typing import Any, Callable, Dict, List, TypeAlias, TypeVar, overload

import numpy as np
from backports.strenum import StrEnum

E = TypeVar("E", bound=StrEnum)
T = TypeVar("T")

RngFactory: TypeAlias = Callable[[], np.random.Generator]


@overload
def choose_enum(rng: np.random.Generator, values: List[E]) -> E:
    pass


@overload
def choose_enum(rng: np.random.Generator, values: List[E], p: Any = None) -> E:
    pass


@overload
def choose_enum(
    rng: np.random.Generator,
    values: List[E],
    p: Any = None,
    size: int | None = None,
    replace: bool = False,
) -> List[E]:
    pass


def choose_enum(
    rng: np.random.Generator,
    values: List[E],
    p: Any = None,
    size: int | None = None,
    replace: bool = False,
) -> E | List[E]:
    if p is not None:
        p = np.array(p) / np.sum(p)

    indxs = rng.choice(a=len(values), size=size, replace=replace, p=p)
    if isinstance(indxs, int):
        return values[indxs]
    else:
        return [values[i] for i in indxs]


@overload
def choose_options(rng: np.random.Generator, options: Dict[T, float] | List[T]) -> T:
    pass


@overload
def choose_options(
    rng: np.random.Generator,
    options: Dict[T, float] | List[T],
    size: int,
) -> List[T]:
    pass


def choose_options(
    rng: np.random.Generator,
    options: Dict[T, float] | List[T],
    size: int | None = None,
) -> T | List[T]:
    if isinstance(options, list):
        options = {o: 1 for o in options}

    items, weights = [], []
    for item, weight in options.items():
        items.append(item)
        weights.append(weight)

    weights = np.array(weights, dtype=float) / np.sum(weights)

    indxs = rng.choice(a=len(items), size=size, replace=False, p=weights)
    if isinstance(indxs, int):
        return items[indxs]
    else:
        return [items[i] for i in indxs]


def resolve_rng(rng: int | RngFactory | None) -> RngFactory:
    if rng is None or isinstance(rng, int):

        def factory():
            return np.random.default_rng(rng)

        return factory
    else:
        return rng


def rng_instance(
    rng: int | RngFactory | np.random.Generator | None,
) -> np.random.Generator:
    if isinstance(rng, np.random.Generator):
        return rng
    else:
        return resolve_rng(rng)()

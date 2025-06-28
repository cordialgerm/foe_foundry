from collections.abc import Hashable
from typing import TypeVar

T = TypeVar("T", bound=Hashable)


def combine_items(
    *items: T | list[T] | set[T], exclude: T | list[T] | set[T] | None = None
) -> list[T]:
    """Combines multiple items or lists of items into a single list, excluding specified items."""
    if exclude is None:
        exclude = set()
    elif isinstance(exclude, list):
        exclude = set(exclude)
    elif not isinstance(exclude, set):
        exclude = {exclude}

    results = set()

    for entry in items:
        if isinstance(entry, (list, set)):
            results.update(entry)
        else:
            results.add(entry)

    return list(results - exclude)

from math import ceil, floor


def easy_multiple_of_five(
    number: float,
    min_val: int | None = None,
    max_val: int | None = None,
) -> int:
    val = 5 * round(number / 5, ndigits=None)

    if min_val is None:
        min_val = 5
    if max_val is None:
        max_val = 10000

    return max(min_val, min(max_val, val))

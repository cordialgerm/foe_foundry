from math import ceil, floor


def easy_multiple_of_five(
    number: float,
    round_down: bool = True,
    min_val: int | None = None,
    max_val: int | None = None,
) -> int:
    if round_down:
        val = int(5 * floor(number / 5.0))
    else:
        val = int(5 * ceil(number / 5.0))

    if min_val is None:
        min_val = 5
    if max_val is None:
        max_val = 10000

    return max(min_val, min(max_val, val))

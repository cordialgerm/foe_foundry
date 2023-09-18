from math import ceil, floor


def easy_multiple_of_five(number: float, round_down: bool = True) -> int:
    if number < 5:
        return 5

    if round_down:
        return int(5 * floor(number / 5.0))
    else:
        return int(5 * ceil(number / 5.0))

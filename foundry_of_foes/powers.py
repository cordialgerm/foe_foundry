def recommended_powers_for_cr(cr: float) -> int:
    if cr <= 1:
        return 0
    elif cr <= 5:
        return 1
    elif cr <= 10:
        return 2
    else:
        return 3

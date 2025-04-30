def recommended_powers_for_cr(cr: float) -> float:
    if cr <= 1:
        return 0.75
    elif cr <= 5:
        return 1.75
    elif cr <= 10:
        return 2.75
    else:
        return 3.25

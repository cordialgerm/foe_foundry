def recommended_powers_for_cr(cr: float) -> float:
    if cr <= 1:
        return 0.5
    elif cr <= 5:
        return 1.5
    elif cr <= 10:
        return 2
    else:
        return 2.5

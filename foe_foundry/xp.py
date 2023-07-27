def xp_by_cr(cr: float) -> int:
    if cr <= 0:
        return 10
    elif cr <= 1 / 8:
        return 25
    elif cr <= 1 / 4:
        return 50
    elif cr <= 1 / 2:
        return 100
    elif cr <= 1:
        return 200
    elif cr <= 2:
        return 450
    elif cr <= 3:
        return 700
    elif cr <= 4:
        return 1100
    elif cr <= 5:
        return 1800
    elif cr <= 6:
        return 2300
    elif cr <= 7:
        return 2900
    elif cr <= 8:
        return 3900
    elif cr <= 9:
        return 5000
    elif cr <= 10:
        return 5900
    elif cr <= 11:
        return 7200
    elif cr <= 12:
        return 8400
    elif cr <= 13:
        return 10000
    elif cr <= 14:
        return 11500
    elif cr <= 15:
        return 13000
    elif cr <= 16:
        return 15000
    elif cr <= 17:
        return 18000
    elif cr <= 18:
        return 20000
    elif cr <= 19:
        return 22000
    elif cr <= 20:
        return 25000
    elif cr <= 21:
        return 33000
    elif cr <= 22:
        return 41000
    elif cr <= 23:
        return 50000
    elif cr <= 24:
        return 62000
    elif cr <= 30:
        return 155000
    else:
        return 155000

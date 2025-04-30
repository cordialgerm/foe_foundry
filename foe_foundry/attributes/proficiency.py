def proficiency_bonus_for_cr(cr: float) -> int:
    # reference data
    # Challenge	Proficiency Bonus
    # 0	+2
    # 1/8	+2
    # 1/4	+2
    # 1/2	+2
    # 1	+2
    # 2	+2
    # 3	+2
    # 4	+2
    # 5	+3
    # 6	+3
    # 7	+3
    # 8	+3
    # 9	+4
    # 10	+4
    # 11	+4
    # 12	+4
    # 13	+5
    # 14	+5
    # 15	+5
    # 16	+5
    # 17	+6
    # 18	+6
    # 19	+6
    # 20	+6
    # 21	+7
    # 22	+7
    # 23	+7
    # 24	+7
    # 25	+8
    # 26	+8
    # 27	+8
    # 28	+8
    # 29	+9
    # 30	+9

    if cr <= 5:
        return 2
    elif cr <= 8:
        return 3
    elif cr <= 12:
        return 4
    elif cr <= 16:
        return 5
    elif cr <= 20:
        return 6
    elif cr <= 24:
        return 7
    elif cr <= 28:
        return 8
    else:
        return 9

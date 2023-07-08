from math import ceil, floor

import numpy as np

from .die import DieFormula


def scale_hp_formula(formula: DieFormula, target: float) -> DieFormula:
    die_types = formula.die_types
    if len(die_types) != 1:
        raise ValueError("HP formula can only use a single die type")
    die_type = die_types[0]
    d = (1 + die_type.as_numeric()) / 2

    n0 = formula.n_die
    c0 = (formula.mod or 0) / n0

    # figure out the maximum hit die needed to get to the target if CON is fixed
    #  x * d + x * c0 = target
    #  x = target / (d + c0)
    n_max = target / (d + c0)

    # figure out the maximum CON needed to get to the target if hit die are fixed
    # n0 * d + n0 * x = target
    # x = (target - n0 * d) / n0
    con_max = (target - n0 * d) / n0

    target_n = n0 + (n_max - n0) / 2
    target_con = c0 + (con_max - c0) / 2

    possibilities = [
        (floor(target_n), floor(target_con)),
        (floor(target_n), ceil(target_con)),
        (ceil(target_n), floor(target_con)),
        (ceil(target_n), ceil(target_con)),
    ]

    formulas, errors = [], []
    for n, c in possibilities:
        formula = DieFormula.from_dict(die_vals={die_type: n}, mod=n * c)
        error = (formula.average - target) ** 2
        formulas.append(formula)
        errors.append(error)

    best_index = np.argmin(errors)
    best_formula = formulas[best_index]
    return best_formula

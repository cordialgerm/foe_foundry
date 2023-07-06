import pytest
from foundry_of_foes.die import DieFormula
from foundry_of_foes.hp import scale_hp_formula


@pytest.mark.parametrize(
    "formula,scale,expected",
    [
        # FoF Minion - 9 (2d8) HP
        (DieFormula(d8=2), 0.8, "2d8 - 2"),  # 7.2 target -> 7 (2d8 -2)
        (DieFormula(d8=2), 0.9, "2d8"),  # 8.1 target -> 9 (2d8)
        (DieFormula(d8=2), 1.3, "2d8 + 2"),  # 11.7 target -> 11 (2d8 + 2)
        # FoF Soldier - 22 (4d8 + 4)
        (DieFormula(d8=4, mod=4), 0.8, "4d8"),  # 17.6 target -> 18 (4d8)
        (DieFormula(d8=4, mod=4), 0.9, "4d8"),  # 19.8 target -> 18 (4d8)
        (DieFormula(d8=4, mod=4), 1.3, "5d8 + 5"),  # 28.6 target -> 27.5 (5d8 + 5)
        # FoF Brute - 45.5 (7d8 + 14)
        (DieFormula(d8=7, mod=14), 0.8, "7d8 + 7"),  # 35.6 target -> 38 (7d8 + 7)
        (DieFormula(d8=7, mod=14), 0.9, "6d8 + 12"),  # 40.05 target -> 39 (6d8 + 12)
        (DieFormula(d8=7, mod=14), 1.3, "9d8 + 18"),  # 59.15 target -> 58.5 (9d8 + 18)
        # FoF Specialist - 84.5 (13d8 + 26)
        (DieFormula(d8=13, mod=26), 0.8, "12d8 + 12"),  # 67.6 target -> 66 (12d8 + 12)
        (DieFormula(d8=13, mod=26), 0.9, "12d8 + 24"),  # 76.05 target -> 78 (12d8 + 24)
        (DieFormula(d8=13, mod=26), 1.3, "15d8 + 45"),  # 109.85 target -> 112.5 (15d8 + 45)
    ],
)
def test_scale_hp_formula(formula: DieFormula, scale: float, expected: str):
    rel_tolerance = 0.075
    abs_tolerance = 5

    target = formula.average * scale
    new_formula = scale_hp_formula(formula, target=target)

    assert (
        new_formula.dice_formula() == expected
    ), f"Failed to scale {formula} to {target:.2f}. Got {new_formula}"

    abs_error = abs(new_formula.average - target)
    rel_error = abs(new_formula.average - target) / target

    assert (
        abs_error <= abs_tolerance or rel_error <= rel_tolerance
    ), f"Failed to scale {formula} to {target:.2f}. Got {new_formula}"

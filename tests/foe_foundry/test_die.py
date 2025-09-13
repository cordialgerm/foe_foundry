from typing import Type

import pytest

from foe_foundry import Die, DieFormula


def test_die_enum():
    assert len(Die.All()) == 6


@pytest.mark.parametrize(
    ["expression", "expected"],
    [("D6 ", Die.d6), (" d12 ", Die.d12), ("d4", Die.d4), ("evil", ValueError)],
)
def test_parse_die(expression: str, expected: Die | Type):
    if isinstance(expected, Die):
        assert Die.parse(expression) == expected
    else:
        with pytest.raises(expected):
            Die.parse(expression)


def test_die_formula_average():
    assert DieFormula(d4=4, mod=4).static == 14
    assert DieFormula(d4=3, mod=4).static == 11
    assert DieFormula(d4=1, d6=2, mod=3).static == 12


def test_die_from_dict():
    die = {
        Die.d6: 8,
    }
    formula = DieFormula.from_dict(die_vals=die)
    assert formula.dice_formula() == "8d6"


def test_increase_decrease():
    dies = Die.All()
    increases = [Die.d6, Die.d8, Die.d10, Die.d12, Die.d20, Die.d20]
    decreases = [Die.d4, Die.d4, Die.d6, Die.d8, Die.d10, Die.d12]

    for d, inc, dec in zip(dies, increases, decreases):
        assert d.increase() == inc
        assert d.decrease() == dec


@pytest.mark.parametrize(
    ["expression", "expected"],
    [
        ("2d8", "2d8"),
        ("6+ 2d20", "2d20 + 6"),
        ("1d20 + 1d20 + 1d20 - 1d20", "2d20"),
        ("1 + 1 + 1 + d4 + d6", "1d4 + 1d6 + 3"),
        ("1 - 1 - 2d20", "-2d20"),
    ],
)
def test_die_from_expressions(expression: str, expected: str):
    die = DieFormula.from_expression(expression)
    assert die.dice_formula() == expected


@pytest.mark.parametrize(
    ["target", "suggested_die", "force_die", "force_even", "expected"],
    [
        (5, Die.d4, None, False, "2d4"),
        (5, None, None, False, "2d4"),
        (6, Die.d6, None, False, "2d4"),
        (20, None, Die.d8, False, "4d8"),
        (20, None, None, False, "8d4"),
        (10, None, Die.d4, True, "4d4"),
        # would normally be 5d4 but force_even should force it to 6d4
        (13, None, Die.d4, True, "6d4"),
        # would normally be 5d4 but force_even should force it to 4d4
        (12.5, None, Die.d4, True, "4d4"),
    ],
)
def test_die_from_target(
    target: float,
    suggested_die: Die | None,
    force_die: Die | None,
    force_even: bool,
    expected: str,
):
    die = DieFormula.target_value(
        target=target,
        suggested_die=suggested_die,
        force_die=force_die,
        force_even=force_even,
    )
    assert die.dice_formula() == expected

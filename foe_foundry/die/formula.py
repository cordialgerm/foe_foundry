from __future__ import annotations

from dataclasses import asdict, dataclass
from math import floor
from typing import List

import d20
import numpy as np

from .expressions import _visit_expression
from .type import Die


@dataclass
class DieFormula:
    d4: int | None = None
    d6: int | None = None
    d8: int | None = None
    d10: int | None = None
    d12: int | None = None
    d20: int | None = None
    mod: int | None = None

    def get(self, die: Die) -> int:
        return getattr(self, die.name) or 0

    @property
    def average(self) -> float:
        return (
            2.5 * (self.d4 or 0)
            + 3.5 * (self.d6 or 0)
            + 4.5 * (self.d8 or 0)
            + 5.5 * (self.d10 or 0)
            + 6.5 * (self.d12 or 0)
            + 10.5 * (self.d20 or 0)
            + (self.mod or 0)
        )

    @property
    def static(self) -> float:
        return floor(self.average)

    @property
    def n_die(self) -> int:
        return (
            (self.d4 or 0)
            + (self.d6 or 0)
            + (self.d8 or 0)
            + (self.d10 or 0)
            + (self.d12 or 0)
            + (self.d20 or 0)
        )

    @property
    def die_types(self) -> List[Die]:
        return [d for d in Die.All() if self.get(d) > 0]

    @property
    def primary_die_type(self) -> Die:
        dies = Die.All()
        scores = [100 * self.get(d) + d.as_numeric() for d in dies]
        index = np.argmax(scores)
        primary_die = dies[index]
        return primary_die

    def dice_formula(self) -> str:
        terms = []
        if self.d4:
            terms.append(f"{self.d4}d4")
        if self.d6:
            terms.append(f"{self.d6}d6")
        if self.d8:
            terms.append(f"{self.d8}d8")
        if self.d10:
            terms.append(f"{self.d10}d10")
        if self.d12:
            terms.append(f"{self.d12}d12")
        if self.d20:
            terms.append(f"{self.d20}d20")

        if len(terms) > 0:
            formula = " + ".join(terms)
            if self.mod is None or self.mod == 0:
                return formula
            elif self.mod > 0:
                return f"{formula} + {self.mod}"
            else:
                return f"{formula} - {abs(self.mod)}"
        else:
            return f"{self.mod or 0}"

    def __str__(self):
        return self.dice_formula()

    def __repr__(self):
        return self.dice_formula()

    def copy(self, **changes) -> DieFormula:
        args = asdict(self)
        args.update(changes)
        return DieFormula(**args)

    @staticmethod
    def from_dict(*, die_vals: dict[Die, int], mod: int = 0) -> DieFormula:
        args = dict(mod=mod)
        for die, n in die_vals.items():
            args[die.name] = n
        return DieFormula(**args)

    @staticmethod
    def from_dice(*, mod: int = 0, **dice: int) -> DieFormula:
        data = {}
        for arg, count in dice.items():
            die = Die.parse(arg)
            data[die] = count
        return DieFormula.from_dict(die_vals=data, mod=mod)

    @staticmethod
    def from_expression(expression: str) -> DieFormula:
        ast = d20.parse(expr=expression, allow_comments=False)
        die_vals, mod = _visit_expression(ast)
        return DieFormula.from_dict(mod=mod, die_vals=die_vals)
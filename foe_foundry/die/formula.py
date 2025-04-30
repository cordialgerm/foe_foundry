from __future__ import annotations

from dataclasses import asdict
from math import ceil, floor
from typing import List

import d20
import numpy as np
from pydantic.dataclasses import dataclass

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

    @property
    def description(self) -> str:
        if self.n_die > 0:
            return f"{self.static} ({self.dice_formula()})"
        else:
            return f"{self.static}"

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

    @staticmethod
    def target_value(
        target: float,
        suggested_die: Die | None = None,
        force_die: Die | None = None,
        per_die_mod: int = 0,
        flat_mod: int = 0,
        min_die_count: int = 0,
        min_val: int = 1,
        force_even: bool = False,
    ) -> DieFormula:
        if suggested_die is None:
            suggested_die = Die.d6

        if force_die is not None:
            candidates = _candidate(
                target, force_die, per_die_mod, flat_mod, min_die_count
            )
        else:
            candidates = (
                _candidate(target, suggested_die, per_die_mod, flat_mod, min_die_count)
                + _candidate(
                    target,
                    suggested_die.decrease(),
                    per_die_mod,
                    flat_mod,
                    min_die_count,
                )
                + _candidate(
                    target,
                    suggested_die.increase(),
                    per_die_mod,
                    flat_mod,
                    min_die_count,
                )
            )

        # sometimes it's required to force the number of dice to be even
        # that way, half of the damage will be a nice number of die to roll
        if force_even:
            even_candidates = []
            for candidate in candidates:
                if candidate.n_die % 2 == 0:
                    even_candidates.append(candidate)
                else:

                    def _even_candidate(mod: int) -> DieFormula:
                        die_type = candidate.primary_die_type
                        n = candidate.n_die + mod
                        return DieFormula.from_dice(
                            **{die_type: n}, mod=flat_mod + n * per_die_mod
                        )

                    even_candidates.append(_even_candidate(1))
                    even_candidates.append(_even_candidate(-1))

            candidates = even_candidates

        # we generally want to be a little below the target because the monsters here are pretty strong
        # so we will give +25% to errors where the average is above the target
        # this will favor rounding down
        errors = [
            1.25 * (c.average - target) if c.average >= target else target - c.average
            for c in candidates
        ]
        best_index = np.argmin(errors)
        candidate = candidates[best_index]

        if candidate.average < min_val:
            return DieFormula.from_expression(str(min_val))
        else:
            return candidate


def _candidate(
    target: float, die: Die, per_die_mod: int, flat_mod: int, min_die_count: int
) -> List[DieFormula]:
    x = (target - flat_mod) / (die.average() + per_die_mod)
    n1 = max(int(ceil(x)), min_die_count)
    n2 = max(int(floor(x)), min_die_count)

    args1 = {str(die): n1, "mod": n1 * per_die_mod + flat_mod}
    args2 = {str(die): n2, "mod": n2 * per_die_mod + flat_mod}

    # require at least 1 damage die
    if n2 >= 1:
        return [DieFormula(**args1), DieFormula(**args2)]
    else:
        return [DieFormula(**args1)]

from __future__ import annotations

from dataclasses import dataclass

from ..die import DieFormula
from .damage_types import DamageType


@dataclass
class Damage:
    formula: DieFormula
    damage_type: DamageType

    def describe(self) -> str:
        return f"{self.formula.static} ({self.formula}) {self.damage_type} damage"

    @staticmethod
    def from_expression(expression: str, damage_type: DamageType = DamageType.Bludgeoning):
        formula = DieFormula.from_expression(expression)
        return Damage(formula=formula, damage_type=damage_type)


@dataclass
class Attack:
    name: str
    hit: int
    damage: Damage
    reach: int = 5
    range: int = 60

    def delta(self, hit_delta: int = 0, dice_delta: int = 0, damage_delta: int = 0) -> Attack:
        new_hit = self.hit + hit_delta

        new_formula = self.damage.formula.copy()

        if dice_delta != 0:
            primary_die = new_formula.primary_die_type
            new_value = new_formula.get(primary_die) + dice_delta
            args = {primary_die.name: new_value}
            new_formula = new_formula.copy(**args)

        if damage_delta != 0:
            n_dice = new_formula.n_die
            new_mod = (new_formula.mod or 0) + n_dice * damage_delta
            new_formula = new_formula.copy(mod=new_mod)

        new_damage = Damage(formula=new_formula, damage_type=self.damage.damage_type)

        return Attack(
            name=self.name, hit=new_hit, damage=new_damage, reach=self.reach, range=self.range
        )

    def describe(self) -> str:
        return f"***{self.name}***. *Ranged or Melee Weapon Attack*: +{self.hit} to hit, reach {self.reach}ft. or range {self.range}ft., one target. *Hit* {self.damage.describe()}."

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import List

from ..die import DieFormula
from .attack_type import AttackType
from .damage_types import DamageType


@dataclass
class Damage:
    formula: DieFormula
    damage_type: DamageType
    description: str = field(init=False)

    def __post_init__(self):
        if self.formula.n_die > 0:
            self.description = (
                f"{self.formula.static} ({self.formula}) {self.damage_type} damage"
            )
        else:
            self.description = f"{self.formula.static} {self.damage_type} damage"

    def __repr__(self) -> str:
        return self.description

    @staticmethod
    def from_expression(expression: str, damage_type: DamageType = DamageType.Bludgeoning):
        formula = DieFormula.from_expression(expression)
        return Damage(formula=formula, damage_type=damage_type)

    def copy(self, **overrides) -> Damage:
        args: dict = dict(formula=self.formula.copy(), damage_type=self.damage_type)
        args.update(overrides)
        return Damage(**args)


@dataclass
class Attack:
    name: str
    hit: int
    damage: Damage
    additional_damage: Damage | None = None
    attack_type: AttackType = AttackType.MeleeNatural
    reach: int | None = 5
    range: int | None = None
    is_melee: bool = field(init=False)

    def __post_init__(self):
        self.is_melee = self.attack_type in {AttackType.MeleeNatural, AttackType.MeleeWeapon}

    def copy(self, **overrides) -> Attack:
        args: dict = dict(
            name=self.name,
            hit=self.hit,
            damage=self.damage.copy(),
            additional_damage=self.additional_damage.copy() if self.additional_damage else None,
            attack_type=self.attack_type,
            reach=self.reach,
            range=self.range,
        )
        args.update(overrides)
        return Attack(**args)

    @property
    def average_damage(self) -> float:
        return self.damage.formula.average + (
            self.additional_damage.formula.average if self.additional_damage is not None else 0
        )

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

    def with_attack_type(self, attack_type: AttackType, damage_type: DamageType) -> Attack:
        new_damage = self.damage.copy(damage_type=damage_type)

        if attack_type in {AttackType.MeleeNatural, AttackType.MeleeWeapon}:
            return self.copy(
                attack_type=attack_type, reach=self.reach or 5, range=None, damage=new_damage
            )
        else:
            return self.copy(
                attack_type=attack_type, range=self.range or 60, reach=None, damage=new_damage
            )

    def describe(self) -> str:
        if self.is_melee:
            description = f"***{self.name}***. *Melee Weapon Attack*: +{self.hit} to hit, reach {self.reach}ft., one target. *Hit* {self.damage.description}"
        else:
            description = f"***{self.name}***. *Ranged Weapon Attack*: +{self.hit} to hit, range {self.range}ft., one target. *Hit* {self.damage.description}"

        if self.additional_damage is not None:
            description += " and " + self.additional_damage.description
        else:
            description += "."

        return description

    def __repr__(self) -> str:
        return self.describe()

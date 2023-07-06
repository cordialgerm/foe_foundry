from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass

from .attributes import Attributes
from .damage import Attack, Damage, DamageType
from .die import DieFormula
from .hp import scale_hp_formula
from .skills import Stats


@dataclass
class ArmorClass:
    value: int
    description: str | None = None

    def delta(self, val: int) -> ArmorClass:
        return ArmorClass(value=self.value + val, description=self.description)


@dataclass
class Movement:
    walk: int
    fly: int | None = None
    climb: int | None = None
    swim: int | None = None
    hover: bool = False


@dataclass
class MonsterDials:
    hp_multiplier: float = 1.0
    ac_modifier: int = 0
    multiattack_modifier: int = 0
    attack_hit_modifier: int = 0
    attack_damage_dice_modifier: int = 0
    attack_damage_modifier: int = 0
    difficulty_class_modifier: int = 0


@dataclass
class BaseStatblock:
    name: str
    cr: float
    ac: ArmorClass
    hp: DieFormula
    speed: Movement
    primary_attribute_score: int
    attributes: Attributes
    attack: Attack
    primary_attribute: Stats = Stats.STR
    multiattack: int = 1
    primary_damage_type: DamageType = DamageType.Bludgeoning
    secondary_damage_type: DamageType | None = None
    difficulty_class_modifier: int = 0

    def __post_init__(self):
        mod = self.attributes.stat_mod(self.primary_attribute) + self.difficulty_class_modifier
        prof = self.attributes.proficiency
        self.difficulty_class = 8 + mod + prof

    def apply_monster_dials(self, dials: MonsterDials) -> BaseStatblock:
        args: dict = dict(
            name=self.name,
            cr=self.cr,
            ac=deepcopy(self.ac),
            hp=deepcopy(self.hp),
            speed=deepcopy(self.speed),
            primary_attribute_score=self.primary_attribute_score,
            attributes=deepcopy(self.attributes),
            attack=deepcopy(self.attack),
            primary_attribute=self.primary_attribute,
            multiattack=self.multiattack,
            primary_damage_type=self.primary_damage_type,
            secondary_damage_type=self.secondary_damage_type,
            difficulty_class_modifier=self.difficulty_class_modifier,
        )

        if dials.hp_multiplier != 1.0:
            new_hp = scale_hp_formula(self.hp, target=self.hp.average * dials.hp_multiplier)
            args.update(hp=new_hp)

        if dials.ac_modifier != 0:
            args.update(ac=self.ac.delta(dials.ac_modifier))

        if dials.multiattack_modifier != 0:
            args.update(multiattack=self.multiattack + dials.multiattack_modifier)

        if (
            dials.attack_hit_modifier != 0
            or dials.attack_damage_dice_modifier != 0
            or dials.attack_damage_modifier != 0
        ):
            delta_args = dict(
                hit_delta=dials.attack_hit_modifier,
                dice_delta=dials.attack_damage_dice_modifier,
                damage_delta=dials.attack_damage_modifier,
            )
            new_attack = self.attack.delta(**delta_args)
            args.update(attack=new_attack)

        if dials.difficulty_class_modifier != 0:
            args.update(difficulty_class_modifier=dials.difficulty_class_modifier)

        return BaseStatblock(**args)

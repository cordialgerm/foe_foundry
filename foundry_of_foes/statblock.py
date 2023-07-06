from __future__ import annotations

from dataclasses import asdict, dataclass

from .attributes import Attributes
from .damage_types import DamageTypes
from .die import DieFormula
from .hp import scale_hp_formula
from .skills import Stats


@dataclass
class ArmorClass:
    value: int
    description: str | None

    def delta(self, val: int) -> ArmorClass:
        return ArmorClass(value=self.value + val, description=self.description)


@dataclass
class Movement:
    walk: int
    fly: int | None
    climb: int | None
    swim: int | None
    hover: bool


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
    primary_damage_type: DamageTypes = DamageTypes.Piercing
    secondary_damage_type: DamageTypes | None = None
    difficulty_class_modifier: int = 0

    def __post_init__(self):
        mod = self.attributes.stat_mod(self.primary_attribute) + self.difficulty_class_modifier
        prof = self.attributes.proficiency
        self.difficulty_class = 8 + mod + prof

    def apply_monster_dials(self, dials: MonsterDials) -> BaseStatblock:
        args = asdict(self)

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

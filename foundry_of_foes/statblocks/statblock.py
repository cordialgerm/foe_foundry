from __future__ import annotations

from dataclasses import dataclass, field

from ..ac import ArmorClass
from ..attributes import Attributes
from ..damage import Attack, DamageType
from ..die import DieFormula
from ..hp import scale_hp_formula
from ..movement import Movement
from ..powers import recommended_powers_for_cr
from ..skills import Stats


@dataclass
class MonsterDials:
    hp_multiplier: float = 1.0
    ac_modifier: int = 0
    multiattack_modifier: int = 0
    attack_hit_modifier: int = 0
    attack_damage_dice_modifier: int = 0
    attack_damage_modifier: int = 0
    difficulty_class_modifier: int = 0
    recommended_powers_modifier: int = 0
    speed_modifier: int = 0
    attribute_modifications: dict = field(default_factory=dict)
    primary_attribute_modifier: int = 0
    primary_attribute: Stats | None = None


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
    recommended_powers_modifier: int = 0

    def __post_init__(self):
        mod = self.attributes.stat_mod(self.primary_attribute) + self.difficulty_class_modifier
        prof = self.attributes.proficiency
        self.difficulty_class = 8 + mod + prof

        self.recommended_powers = (
            recommended_powers_for_cr(self.cr) + self.recommended_powers_modifier
        )

    def apply_monster_dials(self, dials: MonsterDials) -> BaseStatblock:
        args: dict = dict(
            name=self.name,
            cr=self.cr,
            primary_damage_type=self.primary_damage_type,
            secondary_damage_type=self.secondary_damage_type,
        )

        # resolve hp
        args.update(
            hp=self.hp
            if dials.hp_multiplier == 1
            else scale_hp_formula(self.hp, target=self.hp.average * dials.hp_multiplier)
        )

        # resolve ac
        args.update(ac=self.ac.delta(dials.ac_modifier))

        # resolve attack
        args.update(multiattack=self.multiattack + dials.multiattack_modifier)
        args.update(
            attack=self.attack.delta(
                hit_delta=dials.attack_hit_modifier,
                dice_delta=dials.attack_damage_dice_modifier,
                damage_delta=dials.attack_damage_modifier,
            )
        )

        # resolve difficulty class
        args.update(
            difficulty_class_modifier=self.difficulty_class_modifier
            + dials.difficulty_class_modifier
        )

        # resolve speed
        args.update(speed=self.speed.delta(dials.speed_modifier))

        # resolve recommended powers
        args.update(
            recommended_powers_modifier=self.recommended_powers_modifier
            + dials.recommended_powers_modifier
        )

        # resolve attributes
        primary_attribute_score = (
            self.primary_attribute_score + dials.primary_attribute_modifier
        )
        primary_attribute = dials.primary_attribute or self.primary_attribute
        new_attributes = self.attributes.copy(
            **dials.attribute_modifications
        ).update_primary_attribute(
            primary_attribute=primary_attribute, primary_attribute_score=primary_attribute_score
        )
        args.update(
            attributes=new_attributes,
            primary_attribute=primary_attribute,
            primary_attribute_score=primary_attribute_score,
        )

        return BaseStatblock(**args)

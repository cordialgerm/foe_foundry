from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from typing import List, Set

from ..ac import ArmorClass
from ..attributes import Attributes
from ..creature_types import CreatureType
from ..damage import Attack, AttackType, Condition, DamageType
from ..die import DieFormula
from ..hp import scale_hp_formula
from ..movement import Movement
from ..role_types import MonsterRole
from ..senses import Senses
from ..size import Size
from ..skills import Stats
from ..xp import xp_by_cr
from .dials import MonsterDials
from .suggested_powers import recommended_powers_for_cr


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
    multiattack: int = 1
    primary_damage_type: DamageType = DamageType.Bludgeoning
    secondary_damage_type: DamageType | None = None
    difficulty_class_modifier: int = 0
    recommended_powers_modifier: int = 0
    size: Size = Size.Medium
    creature_type: CreatureType = CreatureType.Humanoid
    languages: List[str] = field(default_factory=list)
    senses: Senses = field(default_factory=Senses)
    role: MonsterRole = MonsterRole.Default
    attack_type: AttackType = AttackType.MeleeWeapon
    damage_resistances: Set[DamageType] = field(default_factory=set)
    damage_immunities: Set[DamageType] = field(default_factory=set)
    condition_immunities: Set[Condition] = field(default_factory=set)
    nonmagical_resistance: bool = False
    nonmagical_immunity: bool = False
    difficulty_class_easy: int = field(init=False)

    def __post_init__(self):
        mod = (
            self.attributes.stat_mod(self.attributes.primary_attribute)
            + self.difficulty_class_modifier
        )
        prof = self.attributes.proficiency
        self.difficulty_class = 8 + mod + prof
        self.difficulty_class_easy = self.difficulty_class - 2

        self.recommended_powers = (
            recommended_powers_for_cr(self.cr) + self.recommended_powers_modifier
        )

        self.xp = xp_by_cr(self.cr)

        self.attack = self.attack.with_attack_type(self.attack_type, self.primary_damage_type)

    @property
    def key(self) -> str:
        return self.name.lower().replace(" ", "_")

    @property
    def primary_attribute(self) -> Stats:
        return self.attributes.primary_attribute

    @property
    def selfref(self) -> str:
        return f"the {self.creature_type.value.lower()}"

    @property
    def roleref(self) -> str:
        return f"the {self.role.value.lower()}"

    def __copy_args__(self) -> dict:
        args: dict = dict(
            name=self.name,
            cr=self.cr,
            ac=deepcopy(self.ac),
            hp=deepcopy(self.hp),
            speed=deepcopy(self.speed),
            primary_attribute_score=self.primary_attribute_score,
            attributes=deepcopy(self.attributes),
            attack=deepcopy(self.attack),
            multiattack=self.multiattack,
            primary_damage_type=self.primary_damage_type,
            secondary_damage_type=self.secondary_damage_type,
            difficulty_class_modifier=self.difficulty_class_modifier,
            recommended_powers_modifier=self.recommended_powers_modifier,
            size=self.size,
            creature_type=self.creature_type,
            languages=deepcopy(self.languages),
            senses=deepcopy(self.senses),
            role=self.role,
            attack_type=self.attack_type,
            damage_resistances=deepcopy(self.damage_resistances),
            damage_immunities=deepcopy(self.damage_immunities),
            condition_immunities=deepcopy(self.condition_immunities),
            nonmagical_resistance=self.nonmagical_resistance,
            nonmagical_immunity=self.nonmagical_immunity,
        )
        return args

    def copy(self, **kwargs) -> BaseStatblock:
        args = self.__copy_args__()
        args.update(kwargs)
        return BaseStatblock(**args)

    def apply_monster_dials(self, dials: MonsterDials) -> BaseStatblock:
        args = self.__copy_args__()

        # resolve hp
        if dials.hp_multiplier != 1:
            args.update(
                hp=scale_hp_formula(self.hp, target=self.hp.average * dials.hp_multiplier)
            )

        # resolve ac
        if dials.ac_modifier:
            args.update(ac=self.ac.delta(dials.ac_modifier))

        # resolve attack
        if dials.multiattack_modifier:
            args.update(multiattack=self.multiattack + dials.multiattack_modifier)

        if (
            dials.attack_hit_modifier
            or dials.attack_damage_dice_modifier
            or dials.attack_damage_modifier
        ):
            args.update(
                attack=self.attack.delta(
                    hit_delta=dials.attack_hit_modifier,
                    dice_delta=dials.attack_damage_dice_modifier,
                    damage_delta=dials.attack_damage_modifier,
                )
            )

        # resolve difficulty class
        if dials.difficulty_class_modifier:
            args.update(
                difficulty_class_modifier=self.difficulty_class_modifier
                + dials.difficulty_class_modifier
            )

        # resolve speed
        if dials.speed_modifier:
            args.update(speed=self.speed.delta(dials.speed_modifier))

        # resolve recommended powers
        if dials.recommended_powers_modifier:
            args.update(
                recommended_powers_modifier=self.recommended_powers_modifier
                + dials.recommended_powers_modifier
            )

        return BaseStatblock(**args)

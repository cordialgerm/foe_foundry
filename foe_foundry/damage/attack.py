from __future__ import annotations

from dataclasses import field
from math import ceil, floor

from pydantic.dataclasses import dataclass

from ..die import Die, DieFormula
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
    def from_expression(
        expression: str, damage_type: DamageType = DamageType.Bludgeoning
    ):
        formula = DieFormula.from_expression(expression)
        return Damage(formula=formula, damage_type=damage_type)

    def copy(self, **overrides) -> Damage:
        args: dict = dict(formula=self.formula.copy(), damage_type=self.damage_type)
        args.update(overrides)
        return Damage(**args)


@dataclass(kw_only=True)
class Attack:
    name: str
    display_name: str = ""
    hit: int
    damage: Damage
    additional_damage: Damage | None = None
    attack_type: AttackType = AttackType.MeleeNatural
    reach: int | None = 5
    range: int | None = None
    range_max: int | None = None
    additional_description: str | None = None
    custom_target: str | None = None
    replaces_multiattack: int = 0
    is_equivalent_to_primary_attack: bool = False
    is_melee: bool = field(init=False)
    description: str = field(init=False)

    def __post_init__(self):
        self.is_melee = self.attack_type in {
            AttackType.MeleeNatural,
            AttackType.MeleeWeapon,
        }

        if self.display_name is None or self.display_name == "":
            self.display_name = self.name

        if self.is_melee:
            self.range = None
            self.reach = self.reach if self.reach is not None else 5
        else:
            self.reach = None
            self.range = self.range if self.range is not None else 30

        if self.is_melee:
            attack = "Melee Weapon Attack"
            attack_range = f"reach {self.reach}ft."
        elif self.attack_type in {AttackType.RangedWeapon, AttackType.RangedNatural}:
            attack = "Ranged Weapon Attack"
            if self.range_max is not None:
                attack_range = f"range {self.range}/{self.range_max}ft."
            else:
                attack_range = f"range {self.range}ft."
        elif self.attack_type == AttackType.RangedSpell:
            attack = "Ranged Spell Attack"
            if self.range_max is not None:
                attack_range = f"range {self.range}/{self.range_max}ft."
            else:
                attack_range = f"range {self.range}ft."
        else:
            raise NotImplementedError()

        if self.custom_target is None:
            target = "one target"
        else:
            target = self.custom_target

        description = f"*{attack}*: +{self.hit} to hit, {attack_range}, {target}. *Hit* {self.damage.description}"
        if self.additional_damage is not None:
            description += f" and {self.additional_damage.description}."
        else:
            description += "."

        if self.additional_description is not None:
            description += " " + self.additional_description

        self.description = description

    def copy(self, **overrides) -> Attack:
        if "display_name" in overrides and overrides["display_name"] is None:
            overrides["display_name"] = ""

        args: dict = dict(
            name=self.name,
            display_name=self.display_name,
            hit=self.hit,
            damage=self.damage.copy(),
            additional_damage=self.additional_damage.copy()
            if self.additional_damage
            else None,
            attack_type=self.attack_type,
            reach=self.reach,
            range=self.range,
            range_max=self.range_max,
            custom_target=self.custom_target,
            additional_description=self.additional_description,
            replaces_multiattack=self.replaces_multiattack,
            is_equivalent_to_primary_attack=self.is_equivalent_to_primary_attack,
        )
        args.update(overrides)
        return Attack(**args)

    @property
    def average_damage(self) -> float:
        return self.damage.formula.average + (
            self.additional_damage.formula.average
            if self.additional_damage is not None
            else 0
        )

    @property
    def average_rolled_damage(self) -> float:
        def rolled(d: Damage | None) -> float:
            return d.formula.average - d.formula.static if d is not None else 0

        return rolled(self.damage) + rolled(self.additional_damage)

    def delta(
        self, hit_delta: int = 0, dice_delta: int = 0, damage_delta: int = 0
    ) -> Attack:
        new_hit = self.hit + hit_delta

        new_formula = self.damage.formula.copy()

        if new_formula.n_die + dice_delta <= 0:
            # handle the corner case where the dice_delta is going negative or too small
            # we can't remove dice in this case, so we just make the dice smaller
            primary_die = new_formula.primary_die_type.decrease().decrease().decrease()
            mod = new_formula.mod or 0
            new_formula = DieFormula.from_dice(mod=mod, **{primary_die: 1})
        elif dice_delta != 0:
            primary_die = new_formula.primary_die_type
            new_value = new_formula.get(primary_die) + dice_delta
            args = {primary_die.name: new_value}
            new_formula = new_formula.copy(**args)

        if damage_delta != 0:
            n_dice = new_formula.n_die
            new_mod = (new_formula.mod or 0) + n_dice * damage_delta
            new_formula = new_formula.copy(mod=new_mod)

        new_damage = Damage(formula=new_formula, damage_type=self.damage.damage_type)

        return self.copy(hit=new_hit, damage=new_damage)

    def with_attack_type(
        self, attack_type: AttackType, damage_type: DamageType
    ) -> Attack:
        new_damage = self.damage.copy(damage_type=damage_type)

        if attack_type in {AttackType.MeleeNatural, AttackType.MeleeWeapon}:
            return self.copy(
                attack_type=attack_type,
                reach=self.reach or 5,
                range=None,
                damage=new_damage,
            )
        else:
            return self.copy(
                attack_type=attack_type,
                range=self.range or 60,
                reach=None,
                damage=new_damage,
            )

    def split_damage(
        self, secondary_damage_type: DamageType, split_ratio: float = 0.5
    ) -> Attack:
        # try to split the attack damage to a secondary damage type according to the split_ratio

        primary_damage_type = self.damage.damage_type
        primary_formula = self.damage.formula
        mod = primary_formula.mod or 0
        n_die = primary_formula.n_die
        primary_die = primary_formula.primary_die_type

        if self.additional_damage is not None:
            # it's already been split or modified in some way so don't do anything
            return self.copy()
        elif self.damage.damage_type == secondary_damage_type:
            # if the primary damage type already matches secondary then don't do anything
            return self.copy()
        elif n_die == 1:
            if primary_die >= Die.d6:
                # reduce the damage die by two sizes and add 1d4 additional damage
                new_primary_n_die = 1
                new_secondary_n_die = 1

                if primary_die <= Die.d6:
                    new_primary_die = Die.d4
                else:
                    new_primary_die = primary_die.decrease().decrease()

                new_secondary_die = Die.d4
            else:
                # the die is too small to split so don't do anything
                return self.copy()
        else:
            # if we have more than 1 damage die we can just split the die in half
            # round down so the original damage type is always 50+% of the damage
            new_primary_die = primary_die
            new_secondary_die = primary_die
            new_secondary_n_die = int(floor(n_die * split_ratio))
            new_primary_n_die = n_die - new_secondary_n_die

        new_base_formula = DieFormula.from_dice(
            mod=mod, **{new_primary_die: new_primary_n_die}
        )
        new_secondary_formula = DieFormula.from_dice(
            **{new_secondary_die: new_secondary_n_die}
        )

        new_damage = Damage(formula=new_base_formula, damage_type=primary_damage_type)
        new_secondary_damage = Damage(
            formula=new_secondary_formula, damage_type=secondary_damage_type
        )

        new_attack = self.copy(
            damage=new_damage, additional_damage=new_secondary_damage
        )
        return new_attack

    def join(self) -> Attack:
        """join the additional damage back into the main damage type"""
        if self.additional_damage is None:
            return self.copy()

        damage_type = self.damage.damage_type
        per_die_mod = ceil((self.damage.formula.mod or 0) / self.damage.formula.n_die)
        die = self.damage.formula.primary_die_type
        target_damage = self.average_rolled_damage

        new_damage = Damage(
            formula=DieFormula.target_value(
                target=target_damage, force_die=die, per_die_mod=per_die_mod
            ),
            damage_type=damage_type,
        )

        return self.copy(damage=new_damage, additional_damage=None)

    def scale(
        self,
        *,
        scalar: float,
        mod: int,
        damage_type: DamageType | None = None,
        die: Die | None = None,
        **args,
    ) -> Attack:
        """create a new attack whose average damage is scaled"""
        new_attack = self.join()
        new_target = scalar * new_attack.average_damage
        if die:
            force_die = die
            suggested_die = None
        else:
            force_die = None
            suggested_die = new_attack.damage.formula.primary_die_type

        damage_type = damage_type or new_attack.damage.damage_type
        new_formula = DieFormula.target_value(
            new_target,
            force_die=force_die,
            suggested_die=suggested_die,
            flat_mod=mod,
        )
        new_damage = Damage(formula=new_formula, damage_type=damage_type)
        return new_attack.copy(damage=new_damage, **args)

    def __repr__(self) -> str:
        return self.description

    def __eq__(self, value: object) -> bool:
        return isinstance(value, Attack) and self.name == value.name

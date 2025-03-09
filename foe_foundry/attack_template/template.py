from __future__ import annotations

from dataclasses import dataclass, replace

from numpy.random import Generator

from ..damage import Attack, AttackType, Damage, DamageType
from ..die import Die, DieFormula
from ..statblocks.base import BaseStatblock
from .fix import adjust_attack


@dataclass(kw_only=True)
class AttackTemplate:
    attack_name: str
    display_name: str | None = None
    die: Die
    die_count: int | None = None
    attack_type: AttackType | None = None
    damage_type: DamageType | None = None
    secondary_damage_type: DamageType | None = None
    allows_shield: bool = False
    split_secondary_damage: bool = False
    split_secondary_damage_ratio: float = 0.5
    reach: int | None = None
    range: int | None = None
    range_max: int | None = None
    reach_bonus_for_huge: bool = False
    range_bonus_for_high_cr: bool = False

    def __post_init__(self):
        if self.display_name is None:
            self.display_name = self.attack_name

    def __eq__(self, value: object) -> bool:
        return (
            isinstance(value, AttackTemplate) and value.attack_name == self.attack_name
        )

    def __hash__(self) -> int:
        return hash(self.attack_name)

    def copy(self, **args) -> AttackTemplate:
        return replace(self, **args)

    def with_display_name(self, display_name: str) -> AttackTemplate:
        return self.copy(display_name=display_name)

    def attack_adjustment_args(self, stats: BaseStatblock) -> dict:
        return dict(
            attack_name=self.attack_name,
            attack_display_name=self.display_name,
            attack_type=self.attack_type,
            primary_damage_type=self.damage_type,
            reach=self.reach,
            die=self.die,
            range=self.range,
            range_max=self.range_max,
            reach_bonus_for_huge=self.reach_bonus_for_huge,
            range_bonus_for_high_cr=self.range_bonus_for_high_cr,
            min_die_count=self.die_count or 1,
        )

    def alter_base_stats(self, stats: BaseStatblock) -> BaseStatblock:
        args: dict = dict(uses_shield=self.allows_shield)
        if self.damage_type is not None:
            args.update(primary_damage_type=self.damage_type)
        if self.secondary_damage_type is not None:
            args.update(secondary_damage_type=self.secondary_damage_type)
        return stats.copy(**args)

    def initialize_attack(self, stats: BaseStatblock) -> BaseStatblock:
        # update the attack to help power selection
        primary_attack = adjust_attack(
            stats=stats, attack=stats.attack, **self.attack_adjustment_args(stats)
        )

        return stats.copy(attack=primary_attack)

    def add_as_secondary_attack(
        self,
        stats: BaseStatblock,
        scalar: float = 1.0,
        **attack_args,
    ) -> BaseStatblock:
        return stats.add_attack(
            name=self.attack_name,
            display_name=self.display_name,
            scalar=scalar
            / stats.damage_modifier,  # divide by damage modifier now because it gets added in later
            replaces_multiattack=1,
            is_equivalent_to_primary_attack=True,
            attack_type=self.attack_type,
            damage_type=self.damage_type,
            die=self.die,
            range=self.range,
            range_max=self.range_max,
            reach=self.reach,
            die_count=self.die_count,
            **attack_args,
        )

    def finalize_attacks(
        self,
        stats: BaseStatblock,
        rng: Generator,
        repair_all: bool = True,
    ) -> BaseStatblock:
        if stats.attack.name == self.attack_name:
            attack_to_finalize = stats.attack
            is_primary = True
        else:
            attack_to_finalize = next(
                a for a in stats.additional_attacks if a.name == self.attack_name
            )
            is_primary = False

        # repair the to-hit and damage formulas of the attack
        adjusted_attack = adjust_attack(
            stats=stats,
            attack=attack_to_finalize,
            adjust_to_hit=True,
            adjust_average_damage=True,
            **self.attack_adjustment_args(stats),
        )

        # split damage type on the attack
        if self.split_secondary_damage:
            adjusted_attack = self.split_primary_attack_damage(adjusted_attack, stats)

        # go through secondary attacks and repair to-hit and damage formulas, if appropriate
        additional_attacks = []
        for secondary_attack in stats.additional_attacks:
            if secondary_attack is attack_to_finalize:
                additional_attacks.append(adjusted_attack)
            elif repair_all:
                new_attack = adjust_attack(
                    stats=stats,
                    attack=secondary_attack,
                    die=secondary_attack.damage.formula.primary_die_type,
                    adjust_to_hit=True,
                )
                additional_attacks.append(new_attack)
            else:
                additional_attacks.append(secondary_attack)

        if is_primary:
            return stats.copy(
                attack=adjusted_attack, additional_attacks=additional_attacks
            )
        else:
            return stats.copy(additional_attacks=additional_attacks)

    def add_secondary_damage(
        self, primary_attack: Attack, stats: BaseStatblock
    ) -> Attack:
        if (
            stats.secondary_damage_type is None
            or primary_attack.damage.damage_type == stats.secondary_damage_type
        ):
            return primary_attack.copy()

        current_damage = primary_attack.average_damage
        target_damage = stats.base_attack_damage * stats.damage_modifier
        gap = target_damage - current_damage
        if gap <= 1.5:
            return primary_attack.copy()

        additional_damage = DieFormula.target_value(target=gap, force_die=Die.d4)
        new_additional_damage = Damage(
            formula=additional_damage, damage_type=stats.secondary_damage_type
        )

        new_attack = primary_attack.copy(additional_damage=new_additional_damage)
        return new_attack

    def split_primary_attack_damage(
        self, primary_attack: Attack, stats: BaseStatblock
    ) -> Attack:
        # only split if there is secondary damage
        if (
            stats.secondary_damage_type is None
            or self.damage_type == stats.secondary_damage_type
        ):
            return primary_attack.copy()

        # check the minimum number of damage dice
        # if we're exceeding those, then we can afford to split additional damage
        # if not, we can't split

        # for example, a giant's greatsword should do at least 3d6 slashing
        # so we don't want to split additional secondary damage if it's only doing 3d6 right now

        # in that case, we can try to add additional damage type on top of the minimum damage dice
        min_dice_count = self.die_count or 0
        current_dice_count = primary_attack.damage.formula.n_die
        current_die = primary_attack.damage.formula.primary_die_type
        current_mod = primary_attack.damage.formula.mod or 0
        if current_dice_count <= min_dice_count:
            return self.add_secondary_damage(primary_attack, stats)

        if current_dice_count > 2:
            primary_dice_count = max(
                min_dice_count,
                round(current_dice_count * (1.0 - self.split_secondary_damage_ratio)),
            )
        else:
            primary_dice_count = min_dice_count

        primary_damage_formula = DieFormula.from_dict(
            mod=current_mod, die_vals={current_die: primary_dice_count}
        )
        new_primary_damage = Damage(
            formula=primary_damage_formula,
            damage_type=primary_attack.damage.damage_type,
        )

        # now we need to find out how much room there is to do additional damage
        secondary_dice_count = current_dice_count - primary_dice_count
        available_damage = secondary_dice_count * (1 + current_die.as_numeric()) / 2.0
        secondary_damage_formula = DieFormula.target_value(target=available_damage)
        new_additional_damage = Damage(
            formula=secondary_damage_formula, damage_type=stats.secondary_damage_type
        )

        new_attack = primary_attack.copy(
            damage=new_primary_damage, additional_damage=new_additional_damage
        )
        return new_attack


DefaultAttackTemplate: AttackTemplate = AttackTemplate(attack_name="Attack", die=Die.d6)

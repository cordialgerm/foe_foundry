from numpy.random import Generator

from ..damage import Attack, AttackType, Damage, DamageType
from ..die import Die, DieFormula
from ..size import Size
from ..statblocks.base import BaseStatblock
from .fix import adjust_attack


class AttackTemplate:
    def __init__(
        self,
        *,
        attack_name: str,
        die: Die,
        die_count: int | None = None,
        attack_type: AttackType | None = None,
        damage_type: DamageType | None = None,
        secondary_damage_type: DamageType | None = None,
        allows_shield: bool = False,
        split_secondary_damage: bool = False,
        reach: int | None = None,
        range: int | None = None,
        range_max: int | None = None,
        reach_bonus_for_huge: bool = False,
        range_bonus_for_high_cr: bool = False,
    ):
        self.attack_name = attack_name
        self.attack_type = attack_type
        self.damage_type = damage_type
        self.secondary_damage_type = secondary_damage_type
        self.die = die
        self.die_count = die_count
        self.allows_shield = allows_shield
        self.split_secondary_damage = split_secondary_damage
        self.reach = reach
        self.range = range
        self.range_max = range_max
        self.reach_bonus_for_huge = reach_bonus_for_huge
        self.range_bonus_for_high_cr = range_bonus_for_high_cr

    def attack_adjustment_args(self, stats: BaseStatblock) -> dict:
        return dict(
            attack_name=self.attack_name,
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

    def alter_base_stats(self, stats: BaseStatblock, rng: Generator) -> BaseStatblock:
        args: dict = dict(uses_shield=self.allows_shield)
        if self.attack_type is not None:
            args.update(attack_type=self.attack_type)
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

    def finalize_attacks(self, stats: BaseStatblock, rng: Generator) -> BaseStatblock:
        # repair the to-hit and damage formulas of the primary attack
        primary_attack = adjust_attack(
            stats=stats,
            attack=stats.attack,
            adjust_to_hit=True,
            adjust_average_damage=True,
            **self.attack_adjustment_args(stats),
        )

        # repair the to-hit and damage formulas of the secondary attacks
        additional_attacks = [
            adjust_attack(
                stats=stats, attack=a, die=a.damage.formula.primary_die_type, adjust_to_hit=True
            )
            for a in stats.additional_attacks
        ]

        # split damage type on the primary attack
        if self.split_secondary_damage:
            primary_attack = self.split_primary_attack_damage(primary_attack, stats)

        return stats.copy(attack=primary_attack, additional_attacks=additional_attacks)

    def split_primary_attack_damage(
        self, primary_attack: Attack, stats: BaseStatblock
    ) -> Attack:
        # only split if there is secondary damage
        if (
            stats.secondary_damage_type is None
            or stats.primary_damage_type == stats.secondary_damage_type
        ):
            return primary_attack.copy()

        # check the minimum number of damage dice
        # if we're exceeding those, then we can afford to split additional damage
        # if not, we can't split

        # for example, a giant's greatsword should do at least 3d6 slashing
        # so we don't want to split additional secondary damage if it's only doing 3d6 right now
        min_dice_count = self.die_count or 0
        current_dice_count = primary_attack.damage.formula.n_die
        current_die = primary_attack.damage.formula.primary_die_type
        current_mod = primary_attack.damage.formula.mod or 0
        if current_dice_count <= min_dice_count:
            return primary_attack.copy()

        # now we need to find out how much room there is to do additional damage
        available_damage = (
            (current_dice_count - min_dice_count) * (1 + current_die.as_numeric()) / 2.0
        )

        primary_damage_formula = DieFormula.from_dict(
            mod=current_mod, die_vals={current_die: min_dice_count}
        )
        new_damage = Damage(
            formula=primary_damage_formula, damage_type=primary_attack.damage.damage_type
        )

        secondary_damage_formula = DieFormula.target_value(target=available_damage)
        new_additional_damage = Damage(
            formula=secondary_damage_formula, damage_type=stats.secondary_damage_type
        )

        new_attack = primary_attack.copy(
            damage=new_damage, additional_damage=new_additional_damage
        )
        return new_attack


DefaultAttackTemplate: AttackTemplate = AttackTemplate(attack_name="Attack", die=Die.d6)

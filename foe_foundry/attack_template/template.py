from numpy.random import Generator

from ..damage import AttackType, DamageType
from ..die import Die
from ..statblocks.base import BaseStatblock
from .fix import adjust_attack

# TODO - debilitating conditions should be based on attack templates so refactor all that


class AttackTemplate:
    def __init__(
        self,
        attack_name: str,
        attack_type: AttackType | None = None,
        damage_type: DamageType | None = None,
        secondary_damage_type: DamageType | None = None,
        die: Die | None = None,
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
        self.allows_shield = allows_shield
        self.split_secondary_damage = split_secondary_damage
        self.reach = reach
        self.range = range
        self.range_max = range_max
        self.reach_bonus_for_huge = reach_bonus_for_huge
        self.range_bonus_for_high_cr = range_bonus_for_high_cr

    def attack_adjustment_args(self) -> dict:
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
            stats=stats, attack=stats.attack, **self.attack_adjustment_args()
        )

        return stats.copy(attack=primary_attack)

    def finalize_attacks(self, stats: BaseStatblock, rng: Generator) -> BaseStatblock:
        # repair the to-hit and damage formulas of the primary attack
        primary_attack = adjust_attack(
            stats=stats,
            attack=stats.attack,
            adjust_to_hit=True,
            adjust_average_damage=True,
            **self.attack_adjustment_args()
        )

        # repair the to-hit and damage formulas of the secondary attacks
        additional_attacks = [
            adjust_attack(stats, a, adjust_to_hit=True) for a in stats.additional_attacks
        ]

        # split damage type on the primary attack
        if (
            self.split_secondary_damage
            and stats.secondary_damage_type is not None
            and stats.primary_damage_type != stats.secondary_damage_type
        ):
            primary_attack = primary_attack.split_damage(stats.secondary_damage_type)

        return stats.copy(attack=primary_attack, additional_attacks=additional_attacks)


DefaultAttackTemplate: AttackTemplate = AttackTemplate(attack_name="Attack")

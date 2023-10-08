from numpy.random import Generator

from ..damage import AttackType, DamageType
from ..die import Die
from ..statblocks.base import BaseStatblock
from .fix import adjust_attack


class AttackTemplate:
    def __init__(
        self,
        attack_name: str,
        attack_type: AttackType | None = None,
        damage_type: DamageType | None = None,
        die: Die | None = None,
    ):
        self.attack_name = attack_name
        self.attack_type = attack_type
        self.damage_type = damage_type
        self.die = die

    def alter_base_stats(self, stats: BaseStatblock, rng: Generator) -> BaseStatblock:
        args: dict = {}
        if self.attack_type is not None:
            args.update(attack_type=self.attack_type)
        if self.damage_type is not None:
            args.update(primary_damage_type=self.damage_type)

        if len(args):
            return stats.copy(**args)
        else:
            return stats

    def initialize_attack(self, stats: BaseStatblock) -> BaseStatblock:
        # update the attack to help power selection
        primary_attack = adjust_attack(
            stats=stats,
            attack=stats.attack,
            attack_name=self.attack_name,
            attack_type=self.attack_type,
            primary_damage_type=self.damage_type,
        )

        return stats.copy(attack=primary_attack)

    def finalize_attacks(self, stats: BaseStatblock, rng: Generator) -> BaseStatblock:
        # repair the to-hit and damage formulas of the primary attack
        primary_attack = adjust_attack(
            stats=stats,
            attack=stats.attack,
            attack_name=self.attack_name,
            attack_type=self.attack_type,
            primary_damage_type=self.damage_type,
            die=self.die,
            adjust_to_hit=True,
            adjust_average_damage=True,
        )

        # repair the to-hit and damage formulas of the secondary attacks
        additional_attacks = [
            adjust_attack(stats, a, adjust_to_hit=True) for a in stats.additional_attacks
        ]

        # split damage type on the primary attack
        if stats.secondary_damage_type is not None:
            primary_attack = primary_attack.split_damage(stats.secondary_damage_type)

        return stats.copy(attack=primary_attack, additional_attacks=additional_attacks)


DefaultAttackTemplate: AttackTemplate = AttackTemplate(attack_name="Attack")

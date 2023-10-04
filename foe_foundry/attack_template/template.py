from typing import List

from numpy.random import Generator

from ..damage import Attack, AttackType, Damage, DamageType
from ..die import Die, DieFormula
from ..powers import Power
from ..statblocks.base import BaseStatblock


class AttackTemplate:
    def __init__(
        self,
        attack_name: str | None = None,
        attack_type: AttackType | None = None,
        damage_type: DamageType | None = None,
        die: Die | None = None,
    ):
        self.attack_name = attack_name
        self.attack_type = attack_type
        self.damage_type = damage_type
        self.die = die

    def select_powers(self, stats: BaseStatblock, rng: Generator) -> List[Power]:
        return []

    def alter_base_stats(self, stats: BaseStatblock, rng: Generator) -> BaseStatblock:
        return stats

    def finalize_attacks(self, stats: BaseStatblock, rng: Generator) -> BaseStatblock:
        # repair the to-hit and damage formulas of the primary attack
        primary_attack = adjust_attack(
            stats=stats,
            attack=stats.attack,
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


# helper function to repair an attack
def adjust_attack(
    stats: BaseStatblock,
    attack: Attack,
    attack_name: str | None = None,
    attack_type: AttackType | None = None,
    primary_damage_type: DamageType | None = None,
    die: Die | None = None,
    adjust_to_hit: bool = False,
    adjust_average_damage: bool = False,
) -> Attack:
    args: dict = {}

    if attack_name is not None:
        args.update(name=attack_name)

    # update attack type
    if attack_type is not None:
        args.update(attack_type=attack_type)

    # repair attack to-hit and damage formula
    if adjust_to_hit:
        repaired_hit = stats.attributes.proficiency + stats.attributes.primary_mod
        args.update(hit=repaired_hit)

    # adjust the average damage based on the primary stat mod
    if adjust_average_damage:
        average_damage = attack.damage.formula.average

        if die is None:
            die_args: dict = dict(suggested_die=attack.damage.formula.primary_die_type)
        else:
            die_args: dict = dict(force_die=die)

        repaired_formula = DieFormula.target_value(
            target=average_damage, flat_mod=stats.attributes.primary_mod, **die_args
        )
    else:
        repaired_formula = attack.damage.formula.copy(mod=stats.attributes.primary_mod)

    damage_type = (
        primary_damage_type if primary_damage_type is not None else attack.damage.damage_type
    )
    repaired_damage = Damage(formula=repaired_formula, damage_type=damage_type)
    args.update(damage=repaired_damage)

    new_attack = attack.copy(**args)
    return new_attack

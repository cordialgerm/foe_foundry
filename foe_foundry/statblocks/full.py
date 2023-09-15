from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from ..attributes import Stats
from ..die import DieFormula
from ..features import Feature
from .base import BaseStatblock


@dataclass
class Statblock(BaseStatblock):
    features: List[Feature] = field(default_factory=list)

    @staticmethod
    def from_base_stats(name: str, stats: BaseStatblock, features: List[Feature]) -> Statblock:
        args = stats.__copy_args__()
        args.update(name=name, features=features)

        # repair HP based on CON modifier
        clean_hp = DieFormula.target_value(
            target=stats.hp.average,
            per_die_mod=stats.attributes.stat_mod(Stats.CON),
            suggested_die=stats.size.hit_die(),
        )
        args.update(hp=clean_hp)

        # repair attack to-hit and damage formula
        repaired_hit = stats.attributes.proficiency + stats.attributes.primary_mod
        average_damage = stats.attack.damage.formula.average
        suggested_die = max(stats.attack.damage.formula.primary_die_type, stats.size.hit_die())
        repaired_formula = DieFormula.target_value(
            average_damage, flat_mod=stats.attributes.primary_mod, suggested_die=suggested_die
        )
        repaired_damage = stats.attack.damage.copy(formula=repaired_formula)
        new_attack = stats.attack.copy(hit=repaired_hit, damage=repaired_damage)

        # split damage type
        if stats.secondary_damage_type is not None:
            new_attack = new_attack.split_damage(stats.secondary_damage_type)

        args.update(attack=new_attack)

        return Statblock(**args)

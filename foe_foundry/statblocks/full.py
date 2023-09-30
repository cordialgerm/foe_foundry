from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

import numpy as np

from ..ac import ArmorClassTemplate, ResolvedArmorClass
from ..ac_templates import Unarmored
from ..attributes import Stats
from ..damage import Attack
from ..die import DieFormula
from ..features import Feature
from .base import BaseStatblock


def resolve_ac(templates: List[ArmorClassTemplate], stats: BaseStatblock) -> ResolvedArmorClass:
    if Unarmored not in templates:
        templates.append(Unarmored)

    acs = [t.resolve(stats=stats, uses_shield=stats.uses_shield) for t in templates]
    best_index = np.argmax([a.score for a in acs])
    ac = acs[best_index]
    return ac


@dataclass(kw_only=True)
class Statblock(BaseStatblock):
    ac: ResolvedArmorClass
    features: List[Feature] = field(default_factory=list)

    @staticmethod
    def from_base_stats(name: str, stats: BaseStatblock, features: List[Feature]) -> Statblock:
        ac = resolve_ac(stats.ac_templates, stats=stats)

        args = stats.__copy_args__()
        args.update(name=name, ac=ac, features=features)

        # repair HP based on CON modifier
        clean_hp = DieFormula.target_value(
            target=stats.hp.average,
            per_die_mod=stats.attributes.stat_mod(Stats.CON),
            force_die=stats.size.hit_die(),
        )
        args.update(hp=clean_hp)

        def repair(attack: Attack, adjust_average_damage: bool = True) -> Attack:
            # repair attack to-hit and damage formula
            repaired_hit = stats.attributes.proficiency + stats.attributes.primary_mod
            average_damage = attack.damage.formula.average

            if adjust_average_damage:
                suggested_die = max(
                    attack.damage.formula.primary_die_type, stats.size.hit_die().decrease()
                )
                repaired_formula = DieFormula.target_value(
                    target=average_damage,
                    flat_mod=stats.attributes.primary_mod,
                    suggested_die=suggested_die,
                )
            else:
                repaired_formula = attack.damage.formula.copy(mod=stats.attributes.primary_mod)

            repaired_damage = attack.damage.copy(formula=repaired_formula)
            new_attack = attack.copy(hit=repaired_hit, damage=repaired_damage)
            return new_attack

        # repair the to-hit and damage formulas of the primary attack
        repaired_attack = repair(stats.attack)

        # repair the to-hit and damage formulas of the secondary attacks
        repaired_additional_attacks = [
            repair(a, adjust_average_damage=False) for a in stats.additional_attacks
        ]

        # split damage type on the primary attack
        if stats.secondary_damage_type is not None:
            repaired_attack = repaired_attack.split_damage(stats.secondary_damage_type)

        args.update(attack=repaired_attack, additional_attacks=repaired_additional_attacks)

        return Statblock(**args)

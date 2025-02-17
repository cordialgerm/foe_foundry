from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from typing import List

import numpy as np

from ..ac import ArmorClassTemplate, ResolvedArmorClass
from ..ac_templates import Unarmored
from ..attributes import Stats
from ..die import DieFormula
from ..features import Feature
from .base import BaseStatblock


def resolve_ac(
    templates: List[ArmorClassTemplate], stats: BaseStatblock
) -> ResolvedArmorClass:
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

    def __copy_args__(self) -> dict:
        base_args = super().__copy_args__()
        base_args.update(ac=deepcopy(self.ac), features=deepcopy(self.features))
        return base_args

    def copy(self, **kwargs) -> Statblock:
        args = self.__copy_args__()
        args.update(kwargs)
        return Statblock(**args)

    @staticmethod
    def from_base_stats(
        name: str,
        stats: BaseStatblock,
        features: List[Feature],
    ) -> Statblock:
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

        return Statblock(**args)

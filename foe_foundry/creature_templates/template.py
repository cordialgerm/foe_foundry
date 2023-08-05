from abc import ABC, abstractmethod
from typing import List

import numpy as np

from ..creature_types import CreatureType
from ..powers import Power, PowerType, select_from_powers, select_power
from ..role_types import MonsterRole
from ..roles import AllRoles, RoleTemplate, get_role
from ..statblocks import BaseStatblock, Statblock


class CreatureTypeTemplate(ABC):
    def __init__(self, name: str, creature_type: CreatureType):
        self.name = name
        self.creature_type = creature_type

    @property
    def key(self) -> str:
        return self.name.lower().replace(" ", "_")

    @abstractmethod
    def alter_base_stats(self, stats: BaseStatblock, rng: np.random.Generator) -> BaseStatblock:
        pass

    def select_role(
        self,
        stats: BaseStatblock,
        role_template: RoleTemplate | str | MonsterRole | None,
        rng: np.random.Generator,
    ) -> RoleTemplate:
        if isinstance(role_template, RoleTemplate):
            return role_template
        elif isinstance(role_template, str):
            return get_role(role_template)
        else:
            n = len(AllRoles)
            i = rng.choice(n)
            return AllRoles[i]

    def select_powers(self, stats: BaseStatblock, rng: np.random.Generator) -> List[Power]:
        # TODO - make this scale with CR and let creature types customize this

        # Movement
        movement_power = select_power(stats=stats, power_type=PowerType.Movement, rng=rng)

        # Common
        common_power = select_power(stats=stats, power_type=PowerType.Common, rng=rng)

        # Static
        static_power = select_power(stats=stats, power_type=PowerType.Static, rng=rng)

        # Creature Type
        creature_power = select_power(stats=stats, power_type=PowerType.Creature, rng=rng)

        # Role
        role_power = select_power(stats=stats, power_type=PowerType.Role, rng=rng)

        # Themed
        theme_power = select_power(stats=stats, power_type=PowerType.Theme, rng=rng)

        # Choose Candidates
        candidates = {
            movement_power,
            common_power,
            creature_power,
            role_power,
            static_power,
            theme_power,
        }
        candidates = [c for c in candidates if c is not None]
        multipliers = {
            PowerType.Movement: 0.25,
            PowerType.Common: 0.25,
            PowerType.Creature: 1,
            PowerType.Role: 1,
            PowerType.Static: 0.25,
            PowerType.Theme: 1,
        }
        multipliers = np.array([multipliers[c.power_type] for c in candidates], dtype=float)

        selection = select_from_powers(
            stats, candidates, rng, n=stats.recommended_powers, multipliers=multipliers
        )
        return selection

    def create(
        self,
        stats: BaseStatblock,
        rng: np.random.Generator,
        role_template: RoleTemplate | str | None | MonsterRole = None,
    ) -> Statblock:
        new_stats = self.alter_base_stats(stats, rng)
        role_template = self.select_role(stats=new_stats, role_template=role_template, rng=rng)
        new_stats = role_template.alter_base_stats(new_stats, rng=rng)
        powers = self.select_powers(new_stats, rng)

        features = []
        for power in powers:
            new_stats, feature = power.apply(new_stats, rng)
            features.append(feature)

        name = f"{stats.key}-{self.creature_type}-{role_template.key}"
        stats = Statblock.from_base_stats(name=name, stats=new_stats, features=features)
        return stats

from abc import ABC, abstractmethod
from typing import List, Set, Tuple, overload

import numpy as np

from ..creature_types import CreatureType
from ..features import Feature
from ..powers import Power, PowerType, select_from_powers, select_power, select_powers
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

    def customize_role(self, stats: BaseStatblock, rng: np.random.Generator) -> BaseStatblock:
        return stats.copy()

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

        n = 1 if stats.recommended_powers <= 3 else 2

        # Movement
        movement_power = select_power(stats=stats, power_type=PowerType.Movement, rng=rng)

        # Common
        common_powers = select_powers(stats=stats, power_type=PowerType.Common, rng=rng, n=n)

        # Static
        static_power = select_power(stats=stats, power_type=PowerType.Static, rng=rng)

        # Creature Type
        creature_powers = select_powers(
            stats=stats, power_type=PowerType.Creature, rng=rng, n=n
        )

        # Role
        role_powers = select_powers(
            stats=stats,
            power_type=PowerType.Role,
            rng=rng,
            n=n if len(creature_powers) > 0 else n + 1,
        )

        # Themed
        theme_powers = select_powers(
            stats=stats,
            power_type=PowerType.Theme,
            rng=rng,
            n=n if len(creature_powers) > 0 else n + 1,
        )

        # Choose Candidates
        candidates = (
            {movement_power, static_power}
            | set(common_powers)
            | set(creature_powers)
            | set(role_powers)
            | set(common_powers)
            | set(theme_powers)
        )

        candidates = [c for c in candidates if c is not None]
        multipliers = {
            PowerType.Movement: 0.25,
            PowerType.Common: 0.5,
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

    @overload
    def create(
        self,
        stats: BaseStatblock,
        rng: np.random.Generator,
        role_template: RoleTemplate | str | None | MonsterRole = None,
    ) -> Statblock:
        pass

    @overload
    def create(
        self,
        stats: BaseStatblock,
        rng: np.random.Generator,
        role_template: RoleTemplate | str | None | MonsterRole = None,
        return_features: bool = True,
    ) -> Tuple[Statblock, List[Feature]]:
        pass

    def create(
        self,
        stats: BaseStatblock,
        rng: np.random.Generator,
        role_template: RoleTemplate | str | None | MonsterRole = None,
        return_features: bool = False,
    ) -> Statblock | Tuple[Statblock, List[Feature]]:
        new_stats = self.alter_base_stats(stats, rng)
        role_template = self.select_role(stats=new_stats, role_template=role_template, rng=rng)
        new_stats = role_template.alter_base_stats(new_stats, rng=rng)
        new_stats = self.customize_role(new_stats, rng)

        powers = self.select_powers(new_stats, rng)

        features: Set[Feature] = set()
        for power in powers:
            new_stats, new_features = power.apply(new_stats, rng)

            if isinstance(new_features, Feature):
                new_features = [new_features]

            features.update(new_features)

        name = f"{stats.key}-{self.creature_type}-{role_template.key}"
        stats = Statblock.from_base_stats(name=name, stats=new_stats, features=list(features))

        if return_features:
            return stats, list(features)
        else:
            return stats

from abc import ABC, abstractmethod
from typing import List

import numpy as np

from ..creature_types import CreatureType
from ..powers import Power, PowerType, select_powers
from ..role_types import MonsterRole
from ..roles import AllRoles, RoleTemplate, get_role
from ..statblocks import BaseStatblock, Statblock


class CreatureTypeTemplate(ABC):
    def __init__(self, name: str, creature_type: CreatureType):
        self.name = name
        self.creature_type = creature_type
        self.rng = np.random.default_rng(20210518)

    @property
    def key(self) -> str:
        return self.name.lower().replace(" ", "_")

    @abstractmethod
    def alter_base_stats(self, stats: BaseStatblock) -> BaseStatblock:
        pass

    def select_role(
        self, stats: BaseStatblock, role_template: RoleTemplate | str | MonsterRole | None
    ) -> RoleTemplate:
        if isinstance(role_template, RoleTemplate):
            return role_template
        elif isinstance(role_template, str):
            return get_role(role_template)
        else:
            n = len(AllRoles)
            i = np.random.choice(n)
            return AllRoles[i]

    def select_powers(self, stats: BaseStatblock) -> List[Power]:
        # TODO - make this scale with CR and let creature types customize this

        # Attack - choose 1
        attack_power = select_powers(stats=stats, power_type=PowerType.Attack, rng=self.rng)

        # Movement
        movement_power = select_powers(stats=stats, power_type=PowerType.Movement, rng=self.rng)

        # Common
        common_power = select_powers(stats=stats, power_type=PowerType.Common, rng=self.rng)

        # Role
        # TODO

        # Creature Type
        creature_power = select_powers(stats=stats, power_type=PowerType.Creature, rng=self.rng)

        return [attack_power, movement_power, common_power, creature_power]

    def create(
        self,
        stats: BaseStatblock,
        role_template: RoleTemplate | str | None | MonsterRole = None,
    ) -> Statblock:
        new_stats = self.alter_base_stats(stats)
        role_template = self.select_role(stats=new_stats, role_template=role_template)
        new_stats = role_template.alter_base_stats(new_stats)
        powers = self.select_powers(new_stats)

        features = []
        for power in powers:
            new_stats, feature = power.apply(new_stats)
            features.append(feature)

        name = f"{stats.key}-{self.creature_type}-{role_template.key}"
        stats = Statblock.from_base_stats(name=name, stats=new_stats, features=features)
        return stats

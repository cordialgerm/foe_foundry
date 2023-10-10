from abc import ABC, abstractmethod
from typing import List, Set, Tuple

import numpy as np

from ..attack_template import AttackTemplate, DefaultAttackTemplate
from ..creature_types import CreatureType
from ..features import Feature
from ..powers import Power, PowerType, select_from_powers, select_powers
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

    def select_attack_template(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[AttackTemplate, BaseStatblock]:
        return DefaultAttackTemplate, stats

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

    def select_powers(
        self, stats: BaseStatblock, rng: np.random.Generator, offset: int = 0
    ) -> List[Power]:
        # TODO - make this scale with CR and let creature types customize this

        n = (1 if stats.recommended_powers <= 3 else 2) + offset
        if n <= 0:
            return []

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
        candidates = set(creature_powers) | set(role_powers) | set(theme_powers)

        candidates = [c for c in candidates if c is not None]
        multipliers = {
            PowerType.Creature: 1,
            PowerType.Role: 1,
            PowerType.Theme: 1,
        }
        multipliers = np.array([multipliers[c.power_type] for c in candidates], dtype=float)

        selection = select_from_powers(
            stats, candidates, rng, n=stats.recommended_powers, multipliers=multipliers
        )
        return selection

    def create(
        self,
        base_stats: BaseStatblock,
        rng: np.random.Generator,
        role_template: RoleTemplate | str | None | MonsterRole = None,
    ) -> Statblock:
        # apply creature type modifications
        new_stats = self.alter_base_stats(base_stats, rng)

        # apply role specialization
        role_template = self.select_role(stats=new_stats, role_template=role_template, rng=rng)
        new_stats = role_template.alter_base_stats(new_stats, rng=rng)
        new_stats = self.customize_role(new_stats, rng)

        # apply attack template and attack powers (if any)
        attack_template, new_stats = self.select_attack_template(new_stats, rng)
        if attack_template is not None:
            new_stats = attack_template.alter_base_stats(new_stats, rng)

        # initialize attack to help later power selection
        new_stats = attack_template.initialize_attack(new_stats)

        # select additional powers
        powers = self.select_powers(new_stats, rng)

        # render features from powers
        features: Set[Feature] = set()
        for power in powers:
            new_stats, new_features = power.apply(new_stats, rng)

            if new_features is None:
                new_features = []
            elif isinstance(new_features, Feature):
                new_features = [new_features]

            features.update(new_features)

        # finalize attacks
        new_stats = attack_template.finalize_attacks(new_stats, rng)

        # finalize statblock
        name = f"{base_stats.key}-{self.creature_type}-{role_template.key}"
        stats = Statblock.from_base_stats(name=name, stats=new_stats, features=list(features))
        return stats

from abc import ABC, abstractmethod
from typing import List, Set, Tuple

import numpy as np

from ..attack_template import AttackTemplate, DefaultAttackTemplate
from ..creature_types import CreatureType
from ..powers import select_powers
from ..role_types import MonsterRole
from ..roles import AllRoles, RoleTemplate, get_role
from ..statblocks import BaseStatblock, Statblock
from ..utils.rng import RngFactory, resolve_rng


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

    def customize_attack_template(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> BaseStatblock:
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

    def create(
        self,
        base_stats: BaseStatblock,
        rng_factory: int | RngFactory,
        role_template: RoleTemplate | str | None | MonsterRole = None,
        selection_retries: int = 3,
        skip_power_selection: bool = False,
    ) -> Statblock:
        rng_factory = resolve_rng(rng_factory)

        rng = rng_factory()

        # apply creature type modifications
        new_stats = self.alter_base_stats(base_stats, rng)

        # apply role specialization
        role_template = self.select_role(stats=new_stats, role_template=role_template, rng=rng)
        new_stats = role_template.alter_base_stats(new_stats)
        new_stats = self.customize_role(new_stats, rng)

        # apply attack template and attack powers (if any)
        attack_template, new_stats = self.select_attack_template(new_stats, rng)
        if attack_template is not None:
            new_stats = attack_template.alter_base_stats(new_stats, rng)
            new_stats = self.customize_attack_template(new_stats, rng)

        # initialize attack to help later power selection
        new_stats = attack_template.initialize_attack(new_stats)

        # select additional powers
        if skip_power_selection:
            new_features = []
        else:
            new_stats, new_features = select_powers(
                stats=new_stats,
                rng=rng_factory,
                power_level=new_stats.recommended_powers,
                retries=selection_retries,
            )

        # finalize attacks
        new_stats = attack_template.finalize_attacks(new_stats, rng)

        # finalize statblock
        name = f"{base_stats.key}-{self.creature_type}-{role_template.key}"
        stats = Statblock.from_base_stats(name=name, stats=new_stats, features=new_features)
        return stats

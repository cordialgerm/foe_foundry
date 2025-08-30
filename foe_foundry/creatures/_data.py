from __future__ import annotations

import hashlib
from dataclasses import dataclass, field, replace

import numpy as np

from foe_foundry.powers import Power, SelectionSettings

from ..features import Feature
from ..statblocks import BaseStatblock, Statblock
from ..utils import name_to_key
from .species import CreatureSpecies


@dataclass(kw_only=True, frozen=True)
class StatsBeingGenerated:
    stats: BaseStatblock
    features: list[Feature]
    powers: list[Power]

    def finalize(self) -> Statblock:
        # sort features by action type
        # then sort by whether they are limited use
        # then sort by whether they have recharge

        def sort_key(f: Feature):
            return (
                f.action,
                0
                if f.uses is None and f.recharge is None
                else (f.uses or 0) + (f.recharge or 0),
                f.name,
            )

        features = sorted(self.features, key=sort_key)

        return Statblock.from_base_stats(
            name=self.stats.name, stats=self.stats, features=features
        )


@dataclass(kw_only=True, frozen=True)
class Monster:
    name: str
    cr: float
    is_legendary: bool = False
    srd_creatures: list[str] | None = None
    other_creatures: dict[str, str] | None = None

    def __hash__(self) -> int:
        return hash(self.name)

    @property
    def key(self) -> str:
        return name_to_key(self.name)


@dataclass(kw_only=True, frozen=True)
class MonsterVariant:
    name: str
    description: str
    monsters: list[Monster]

    def __hash__(self) -> int:
        return hash(self.name)

    @property
    def key(self) -> str:
        return name_to_key(self.name)


@dataclass(kw_only=True, frozen=True)
class GenerationSettings:
    creature_name: str
    monster_template: str
    monster_key: str
    cr: float
    is_legendary: bool
    variant: MonsterVariant
    monster: Monster
    species: CreatureSpecies | None = None
    rng: np.random.Generator

    hp_multiplier: float = 1.0
    damage_multiplier: float = 1.0

    power_weights: dict[str, float] = field(default_factory=dict)

    def __post_init__(self):
        if self.rng is None:
            object.__setattr__(self, "rng", rng_factory(self.monster, self.species))

    @property
    def key(self) -> str:
        if self.species is not None:
            n = f"{self.species.key}-{self.monster_key}"
        else:
            n = self.creature_name

        return n.lower().replace(" ", "-")

    @property
    def id(self) -> str:
        return self.key

    @property
    def selection_settings(self) -> SelectionSettings:
        power_weights = {name_to_key(p): w for p, w in self.power_weights.items()}
        return SelectionSettings(rng=self.rng, power_weights=power_weights)

    def copy(self, **args) -> GenerationSettings:
        return replace(self, **args)


def rng_factory(monster: Monster, species: CreatureSpecies | None):
    hash_key = f"{monster.name}-{species.name}" if species is not None else monster.name
    bytes = hashlib.sha256(hash_key.encode("utf-8")).digest()
    random_state = int.from_bytes(bytes, byteorder="little")
    return np.random.default_rng(seed=random_state)

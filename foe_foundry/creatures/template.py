from __future__ import annotations

import hashlib
from dataclasses import dataclass, field, replace
from typing import Callable, Iterable, TypeAlias

import numpy as np

from ..features import Feature
from ..powers.selection import PowerSelector, SelectionSettings
from ..statblocks import BaseStatblock, Statblock
from ..utils import name_to_key


@dataclass(kw_only=True, frozen=True)
class StatsBeingGenerated:
    stats: BaseStatblock
    features: list[Feature]
    powers: PowerSelector

    def finalize(self) -> Statblock:
        return Statblock.from_base_stats(
            name=self.stats.name, stats=self.stats, features=self.features
        )


@dataclass(kw_only=True, frozen=True)
class SuggestedCr:
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
class CreatureVariant:
    name: str
    description: str
    suggested_crs: list[SuggestedCr]

    def __hash__(self) -> int:
        return hash(self.name)

    @property
    def key(self) -> str:
        return name_to_key(self.name)


@dataclass(kw_only=True, frozen=True)
class CreatureSpecies:
    name: str
    description: str

    def alter_base_stats(self, stats: BaseStatblock) -> BaseStatblock:
        return stats

    def __hash__(self) -> int:
        return hash(self.name)


@dataclass(kw_only=True, frozen=True)
class GenerationSettings:
    creature_name: str
    cr: float
    variant: CreatureVariant
    species: CreatureSpecies | None = None
    rng: np.random.Generator

    selection_settings: SelectionSettings = field(default_factory=SelectionSettings)
    hp_multiplier: float = 1.0
    damage_multiplier: float = 1.0

    power_boosts: dict[str, float] = field(default_factory=dict)
    theme_boosts: dict[str, float] = field(default_factory=dict)

    @property
    def key(self) -> str:
        if self.species is not None:
            n = f"{self.creature_name}-{self.species.name}"
        else:
            n = self.creature_name

        return n.lower().replace(" ", "-")

    @property
    def id(self) -> str:
        return self.key

    def copy(self, **args) -> GenerationSettings:
        return replace(self, **args)


GenerateCallback: TypeAlias = Callable[[GenerationSettings], StatsBeingGenerated]


@dataclass(kw_only=True)
class CreatureTemplate:
    name: str
    tag_line: str
    description: str
    environments: list[str]  # TODO - standardize
    treasure: list[str]
    variants: list[CreatureVariant]
    species: list[CreatureSpecies]
    callback: GenerateCallback

    def __post_init__(self):
        self.n_variant = len(self.variants)
        self._variant_map = {v.name: v for v in self.variants}
        self.n_species = len(self.species)
        self._species_map = {s.name: s for s in self.species}

        srd_creatures = set()
        other_creatures = set()
        for v in self.variants:
            for s in v.suggested_crs:
                if s.srd_creatures is not None:
                    srd_creatures.update(s.srd_creatures)
                if s.other_creatures is not None:
                    other_creatures.update(s.other_creatures.keys())
        self.srd_ceatures = sorted(list(srd_creatures))
        self.other_creatures = sorted(list(other_creatures))

    @property
    def key(self) -> str:
        return name_to_key(self.name)

    def __hash__(self) -> int:
        return hash(self.name)

    def generate(self, settings: GenerationSettings) -> StatsBeingGenerated:
        return self.callback(settings)

    def generate_all(self, **kwargs) -> Iterable[StatsBeingGenerated]:
        for settings in self.generate_settings(**kwargs):
            yield self.generate(settings)

    def generate_settings(self, **kwargs) -> list[GenerationSettings]:
        options = []
        for variant in self.variants:
            for suggested_cr in variant.suggested_crs:
                for species in self.species if self.n_species > 0 else [None]:
                    hash_key = (
                        f"{suggested_cr.name}-{species.name}"
                        if species is not None
                        else suggested_cr.name
                    )

                    def rng_factory() -> np.random.Generator:
                        bytes = hashlib.sha256(hash_key.encode("utf-8")).digest()
                        random_state = int.from_bytes(bytes, byteorder="little")
                        return np.random.default_rng(seed=random_state)

                    args: dict = (
                        dict(
                            creature_name=suggested_cr.name,
                            cr=suggested_cr.cr,
                            variant=variant,
                            species=species,
                            selection_settings=SelectionSettings(),
                            rng=rng_factory(),
                        )
                        | kwargs
                    )

                    options.append(GenerationSettings(**args))
        return options

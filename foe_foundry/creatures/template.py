import hashlib
from dataclasses import dataclass
from typing import Callable, Iterable, TypeAlias, cast

import numpy as np

from ..features import Feature
from ..powers.selection import PowerSelector
from ..statblocks import BaseStatblock, Statblock
from ..utils.rng import RngFactory


@dataclass(kw_only=True)
class StatsBeingGenerated:
    stats: BaseStatblock
    features: list[Feature]
    powers: PowerSelector

    def finalize(self) -> Statblock:
        return Statblock.from_base_stats(
            name=self.stats.name, stats=self.stats, features=self.features
        )


GenerateCallback: TypeAlias = Callable[..., StatsBeingGenerated]


@dataclass(kw_only=True)
class SuggestedCr:
    name: str
    cr: float
    is_legendary: bool = False
    srd_creatures: list[str] | None = None
    other_creatures: dict[str, str] | None = None


@dataclass(kw_only=True)
class CreatureVariant:
    name: str
    description: str
    suggested_crs: list[SuggestedCr]


@dataclass(kw_only=True)
class CreatureSpecies:
    name: str
    description: str

    def alter_base_stats(self, stats: BaseStatblock) -> BaseStatblock:
        return stats


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

    def generate(
        self,
        name: str,
        cr: float,
        rng_factory: RngFactory,
        variant_name: str | None = None,
        species_name: str | None = None,
    ) -> StatsBeingGenerated:
        rng = rng_factory()

        if variant_name is None:
            variant_name = cast(str, rng.choice(list(self._variant_map.keys())))

        if species_name is None and self.n_species > 0:
            species_name = cast(str, rng.choice(list(self._species_map.keys())))

        variant = self._variant_map[variant_name]
        species = self._species_map[species_name] if species_name else None

        return self.callback(
            name=name, variant=variant, species=species, rng=rng, cr=cr
        )

    def generate_all(self) -> Iterable[StatsBeingGenerated]:
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

                    yield self.generate(
                        name=suggested_cr.name,
                        cr=suggested_cr.cr,
                        rng_factory=rng_factory,
                        variant_name=variant.name,
                        species_name=species.name if species is not None else None,
                    )

    def generate_options(self) -> list[dict]:
        options = []
        for variant in self.variants:
            for suggested_cr in variant.suggested_crs:
                for species in self.species if self.n_species > 0 else [None]:
                    options.append(
                        dict(
                            name=suggested_cr.name,
                            cr=suggested_cr.cr,
                            variant_name=variant.name,
                            species_name=species.name if species else None,
                        )
                    )
        return options

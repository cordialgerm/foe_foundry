from __future__ import annotations

import hashlib
from dataclasses import dataclass, field, replace
from functools import cached_property
from pathlib import Path
from typing import Callable, Iterable, TypeAlias

import numpy as np

from foe_foundry.utils import find_image, find_lore
from foe_foundry.utils.monster_content import extract_tagline, strip_yaml_frontmatter

from ..features import Feature
from ..powers.selection import PowerSelector, SelectionSettings
from ..statblocks import BaseStatblock, Statblock
from ..utils import name_to_key
from .species import CreatureSpecies


@dataclass(kw_only=True, frozen=True)
class StatsBeingGenerated:
    stats: BaseStatblock
    features: list[Feature]
    powers: PowerSelector

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
    species: CreatureSpecies | None = None
    rng: np.random.Generator

    selection_settings: SelectionSettings = field(default_factory=SelectionSettings)
    hp_multiplier: float = 1.0
    damage_multiplier: float = 1.0

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

    def copy(self, **args) -> GenerationSettings:
        return replace(self, **args)


GenerateCallback: TypeAlias = Callable[[GenerationSettings], StatsBeingGenerated]


@dataclass(kw_only=True)
class MonsterTemplate:
    name: str
    tag_line: str
    description: str
    environments: list[str]  # TODO - standardize
    treasure: list[str]
    variants: list[MonsterVariant]
    species: list[CreatureSpecies]
    callback: GenerateCallback
    is_sentient_species: bool = False
    lore_md: str | None = field(init=False)

    def __post_init__(self):
        self.n_variant = len(self.variants)
        self._variant_map = {v.key: v for v in self.variants}
        self.n_species = len(self.species)

        srd_creatures = set()
        other_creatures = set()
        for v in self.variants:
            for s in v.monsters:
                if s.srd_creatures is not None:
                    srd_creatures.update(s.srd_creatures)
                if s.other_creatures is not None:
                    other_creatures.update(s.other_creatures.keys())
        self.srd_ceatures = sorted(list(srd_creatures))
        self.other_creatures = sorted(list(other_creatures))

        # update tag line from lore, if available
        lore_path = find_lore(self.key)
        if lore_path is not None:
            lore_md = strip_yaml_frontmatter(lore_path.read_text(encoding="utf-8"))
            tagline = extract_tagline(lore_md)
            if tagline is not None:
                self.tag_line = tagline.strip()
            self.lore_md = lore_md
        else:
            self.lore_md = None

    @cached_property
    def image_urls(self) -> dict[str, list[Path]]:
        urls = {}
        for variant in self.variants:
            image_urls = find_image(variant.key)
            if len(image_urls) == 0:
                image_urls = find_image(self.key)
            urls[variant.key] = image_urls
        return urls

    @cached_property
    def primary_image_url(self) -> Path | None:
        urls = self.image_urls.get(self.key)
        if urls is None:
            return None

        return urls[0] if len(urls) else None

    def get_images(self, variant: str) -> list[Path]:
        if variant not in self._variant_map:
            raise ValueError(f"Variant {variant} not found in template {self.name}")

        variant_images = self.image_urls.get(variant, [])
        if len(variant_images) == 0:
            return self.image_urls.get(self.key, [])
        else:
            return variant_images

    @property
    def key(self) -> str:
        return name_to_key(self.name)

    def __hash__(self) -> int:
        return hash(self.name)

    def generate(self, settings: GenerationSettings) -> StatsBeingGenerated:
        """Creates a statblock for the given generation settings"""
        return self.callback(settings)

    def generate_monster(
        self,
        variant: MonsterVariant,
        monster: Monster,
        species: CreatureSpecies | None = None,
        **kwargs,
    ) -> StatsBeingGenerated:
        """Creates a statblock for the given suggested CR"""

        if species is None or species.key == "human":
            creature_name = monster.name
        else:
            creature_name = f"{species.name} {monster.name}"

        args: dict = (
            dict(
                creature_name=creature_name,
                monster_template=self.name,
                monster_key=monster.key,
                cr=monster.cr,
                is_legendary=monster.is_legendary,
                variant=variant,
                species=species,
                selection_settings=SelectionSettings(),
                rng=rng_factory(monster, species),
            )
            | kwargs
        )

        settings = GenerationSettings(**args)
        return self.generate(settings)

    def generate_all(self, **kwargs) -> Iterable[StatsBeingGenerated]:
        """Generate one instance of a statblock for each variant and suggested CR in this template"""
        for settings in self.generate_settings(**kwargs):
            yield self.generate(settings)

    def generate_settings(self, **kwargs) -> list[GenerationSettings]:
        """Generates all possible settings for this template"""
        options = []
        for variant in self.variants:
            for monster in variant.monsters:
                for species in self.species if self.n_species > 0 else [None]:
                    args: dict = (
                        dict(
                            creature_name=monster.name,
                            monster_template=self.name,
                            monster_key=monster.key,
                            cr=monster.cr,
                            is_legendary=monster.is_legendary,
                            variant=variant,
                            species=species,
                            selection_settings=SelectionSettings(),
                            rng=rng_factory(monster, species),
                        )
                        | kwargs
                    )

                    options.append(GenerationSettings(**args))
        return options


def rng_factory(monster: Monster, species: CreatureSpecies | None):
    hash_key = f"{monster.name}-{species.name}" if species is not None else monster.name
    bytes = hashlib.sha256(hash_key.encode("utf-8")).digest()
    random_state = int.from_bytes(bytes, byteorder="little")
    return np.random.default_rng(seed=random_state)

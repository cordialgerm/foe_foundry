from __future__ import annotations

from abc import abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from functools import cached_property
from pathlib import Path
from typing import Iterable

from git import GitError, Repo

from foe_foundry.attack_template import AttackTemplate
from foe_foundry.environs import EnvironmentAffinity
from foe_foundry.features import Feature
from foe_foundry.powers import PowerSelection
from foe_foundry.powers.legendary import get_legendary_actions
from foe_foundry.utils import find_image, find_lore
from foe_foundry.utils.monster_content import extract_tagline, strip_yaml_frontmatter

from ..statblocks import BaseStatblock, Statblock  # noqa
from ..utils import name_to_key
from ._data import (
    GenerationSettings,
    Monster,
    MonsterVariant,
    StatsBeingGenerated,
    rng_factory,
)
from .species import CreatureSpecies


@dataclass(kw_only=True)
class MonsterTemplate:
    name: str
    tag_line: str
    description: str
    treasure: list[str]
    variants: list[MonsterVariant]
    species: list[CreatureSpecies]
    environments: list[EnvironmentAffinity] = field(default_factory=list)
    is_sentient_species: bool = False
    lore_md: str | None = field(init=False)
    create_date: datetime = field(init=False)
    modified_date: datetime = field(init=False)

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

        # Set create_date and modified_date using helper
        monster_file = (
            Path.cwd()
            / "foe_foundry"
            / "creatures"
            / self.key.replace("-", "_")
            / f"{self.key.replace('-', '_')}.py"
        )
        self.create_date = self._get_git_date(monster_file, first_commit=True)
        self.modified_date = self._get_git_date(monster_file, first_commit=False)

    @cached_property
    def image_urls(self) -> dict[str, list[Path]]:
        urls = {}
        urls[self.key] = find_image(self.key)
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

    def _get_git_date(self, monster_file: Path, first_commit: bool = True) -> datetime:
        """Helper to get git commit date for a file. If first_commit is True, gets the oldest commit (creation); else, gets the most recent (modified)."""
        if not monster_file.exists():
            raise ValueError(
                f"Monster file does not exist: {monster_file}. "
                "Ensure the monster template is correctly defined."
            )
        try:
            repo = Repo(Path.cwd())
            # first_commit=True: oldest commit, first=True; else, most recent commit, reverse=True
            commits = list(repo.iter_commits(paths=str(monster_file)))
            if commits:
                commit = commits[-1] if first_commit else commits[0]
                date = commit.committed_datetime
                if date.tzinfo is None:
                    date = date.replace(tzinfo=timezone.utc)
            else:
                date = datetime.now(timezone.utc)
        except (GitError, Exception) as x:
            raise ValueError(f"Failed to get git date for {monster_file}: {x}") from x
        return date

    def __hash__(self) -> int:
        return hash(self.name)

    def generate(self, settings: GenerationSettings) -> StatsBeingGenerated:
        """Creates a statblock for the given generation settings"""

        stats, attacks = self.generate_stats(settings)

        # INITIALIZE ATTACKS
        primary_attack = attacks[0]
        stats = primary_attack.alter_base_stats(stats)
        stats = primary_attack.initialize_attack(stats)
        if len(attacks) > 1:
            for secondary_attack in attacks[1:]:
                stats = secondary_attack.add_as_secondary_attack(stats)

        # POWERS
        power_selection = self.choose_powers(settings)
        powers = power_selection.choose_powers(settings.selection_settings)

        # SPECIES CUSTOMIZATION
        if settings.species is not None:
            stats = settings.species.alter_base_stats(stats)

        # POWERS
        features: list[Feature] = []
        for power in powers:
            stats = power.modify_stats(stats)
            features += power.generate_features(stats)

        # ATTACKS
        for attack in attacks:
            stats = attack.finalize_attacks(stats, settings.rng, repair_all=False)

        # LEGENDARY ATTACKS
        if stats.is_legendary:
            legendary_features = get_legendary_actions(stats, features)
            features += legendary_features

        return StatsBeingGenerated(stats=stats, features=features, powers=powers)

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
                monster=monster,
                species=species,
                rng=rng_factory(monster, species),
            )
            | kwargs
        )

        settings = GenerationSettings(**args)
        return self.generate(settings)

    def generate_all(
        self, **kwargs
    ) -> Iterable[
        tuple[MonsterVariant, Monster, CreatureSpecies | None, StatsBeingGenerated]
    ]:
        """Generate one instance of a statblock for each variant and suggested CR in this template"""
        for settings in self.generate_settings(**kwargs):
            stats = self.generate(settings)
            yield settings.variant, settings.monster, settings.species, stats

    def generate_settings(self, **kwargs) -> Iterable[GenerationSettings]:
        """Generates all possible settings for this template"""
        for variant in self.variants:
            for monster in variant.monsters:
                for species in self.species if self.n_species > 0 else [None]:
                    settings = self._settings_for_variant(
                        variant, monster, species, **kwargs
                    )
                    yield settings

    def _settings_for_variant(
        self,
        variant: MonsterVariant,
        monster: Monster,
        species: CreatureSpecies | None,
        **kwargs,
    ) -> GenerationSettings:
        args: dict = (
            dict(
                creature_name=monster.name,
                monster_template=self.name,
                monster_key=monster.key,
                cr=monster.cr,
                is_legendary=monster.is_legendary,
                variant=variant,
                monster=monster,
                species=species,
                rng=rng_factory(monster, species),
            )
            | kwargs
        )
        return GenerationSettings(**args)

    @abstractmethod
    def choose_powers(self, settings: GenerationSettings) -> PowerSelection:
        pass

    @abstractmethod
    def generate_stats(
        self, settings: GenerationSettings
    ) -> tuple[BaseStatblock, list[AttackTemplate]]:
        pass

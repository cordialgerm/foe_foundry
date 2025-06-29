from __future__ import annotations

from dataclasses import dataclass, replace
from typing import TypeAlias

import inflect
import numpy as np

from foe_foundry.creatures import (
    AllSpecies,
    AllTemplates,
    CreatureSpecies,
    Monster,
    MonsterTemplate,
    MonsterVariant,
)
from foe_foundry.utils import name_to_key

MonsterInfo: TypeAlias = tuple[MonsterTemplate, MonsterVariant | None, Monster | None]

p = inflect.engine()


@dataclass(kw_only=True, frozen=True, eq=False)
class MonsterRef:
    """A reference to a monster template or variant."""

    original_monster_name: str
    template: MonsterTemplate
    variant: MonsterVariant | None = None
    monster: Monster | None = None
    species: CreatureSpecies | None = None

    def copy(self, **args) -> MonsterRef:
        """Creates a copy of the monster reference with updated values."""
        return replace(self, **args)

    def resolve(self) -> MonsterRef:
        if self.variant is not None:
            return self

        variant = self.template.variants[0]
        monster = variant.monsters[0]
        return replace(self, variant=variant, monster=monster)

    def __hash__(self) -> int:
        return hash(
            (
                self.original_monster_name,
                self.template.key,
                self.variant.key if self.variant else None,
                self.monster.key if self.monster else None,
                self.species.key if self.species else None,
            )
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, MonsterRef):
            return NotImplemented
        return (
            self.original_monster_name == other.original_monster_name
            and self.template.key == other.template.key
            and (self.variant.key if self.variant else None) == (other.variant.key if other.variant else None)
            and (self.monster.key if self.monster else None) == (other.monster.key if other.monster else None)
            and (self.species.key if self.species else None) == (other.species.key if other.species else None)
        )


class MonsterRefResolver:
    """Resolves a monster name to a template, variant, and suggested CR."""

    def __init__(self):
        lookup: dict[str, MonsterInfo] = {}
        alias_lookup: dict[str, list[MonsterInfo]] = {}
        species_lookup: dict[str, CreatureSpecies] = {s.key: s for s in AllSpecies}

        for template in AllTemplates:
            lookup[template.key] = (template, None, None)
            for variant in template.variants:
                for monster in variant.monsters:
                    lookup[monster.key] = (template, variant, monster)

                    if monster.srd_creatures is not None:
                        for alias in monster.srd_creatures:
                            alias = name_to_key(alias)
                            if alias not in alias_lookup:
                                alias_lookup[alias] = []
                            alias_lookup[alias].append((template, variant, monster))

                    if monster.other_creatures is not None:
                        for other_creature, _ in monster.other_creatures.items():
                            alias = name_to_key(other_creature)
                            if alias not in alias_lookup:
                                alias_lookup[alias] = []
                            alias_lookup[alias].append((template, variant, monster))

        self.lookup = lookup
        self.aliases = alias_lookup
        self.species_lookup = species_lookup

    def resolve_monster_ref(
        self, monster_name: str, rng: np.random.Generator | None = None
    ) -> MonsterRef | None:
        """Resolves a monster name to a template, variant, and suggested CR."""

        if rng is None:
            rng = np.random.default_rng()

        original_monster_name = monster_name

        ref = self._resolve_monster_ref_inner(
            original_monster_name=original_monster_name,
            monster_name=monster_name,
            rng=rng,
        )
        if ref is not None:
            return ref

        singular = p.singular_noun(monster_name)  # type: ignore
        if singular:
            monster_name = singular

        return self._resolve_monster_ref_inner(
            original_monster_name=original_monster_name,
            monster_name=monster_name,
            rng=rng,
        )

    def _resolve_species_from_monster_name(
        self, monster_name: str
    ) -> tuple[CreatureSpecies | None, str | None]:
        """Check if the monster name starts with a species name, like an Orc Berserker"""

        separators = [" ", "-", "_"]
        if not any(sep in monster_name for sep in separators):
            return None, None

        for sep in separators:
            if sep not in monster_name:
                continue

            species_name = monster_name.split(sep)[0]
            rest_of_name = monster_name[len(species_name) + 1 :]
            species = self.species_lookup.get(species_name)
            if species is not None:
                return species, rest_of_name

        return None, None

    def _resolve_monster_ref_inner(
        self,
        *,
        original_monster_name: str,
        monster_name: str,
        species_key: str | None = None,
        rng: np.random.Generator,
    ) -> MonsterRef | None:
        """Resolves a monster name to a template, variant, and suggested CR."""

        monster_name = monster_name.strip().lower()
        species = self.species_lookup.get(species_key) if species_key else None

        ref = self._resolve_monster_key(
            original_monster_name=original_monster_name,
            monster_name=monster_name,
            species_key=species_key,
        )
        ref_alias = self._resolve_alias(
            original_monster_name=original_monster_name,
            monster_name=monster_name,
            species_key=species_key,
            rng=rng,
        )

        if ref is not None and ref.monster is not None:
            return ref
        elif ref is not None and ref.monster is None and ref_alias is not None:
            return ref_alias
        elif ref is not None:
            return ref
        elif ref_alias is not None:
            return ref_alias

        species, rest_of_name = self._resolve_species_from_monster_name(monster_name)
        if species is None or rest_of_name is None:
            return None
        return self._resolve_monster_ref_inner(
            original_monster_name=original_monster_name,
            monster_name=rest_of_name,
            species_key=species.key if species else None,
            rng=rng,
        )

    def _resolve_monster_key(
        self,
        *,
        original_monster_name: str,
        monster_name: str,
        species_key: str | None = None,
    ) -> MonsterRef | None:
        monster_name = monster_name.strip().lower()
        key = name_to_key(monster_name)
        species = self.species_lookup.get(species_key) if species_key else None

        monster_info = self.lookup.get(key)
        if monster_info is None:
            return None

        template, variant, monster = monster_info
        return MonsterRef(
            original_monster_name=original_monster_name,
            template=template,
            variant=variant,
            monster=monster,
            species=species,
        )

    def _resolve_alias(
        self,
        *,
        original_monster_name: str,
        monster_name: str,
        species_key: str | None = None,
        rng: np.random.Generator,
    ) -> MonsterRef | None:
        monster_name = monster_name.strip().lower()
        key = name_to_key(monster_name)
        species = self.species_lookup.get(species_key) if species_key else None

        monster_infos = self.aliases.get(key)
        if not monster_infos:
            return None

        index = rng.choice(len(monster_infos))
        monster_info = monster_infos[index]
        template, variant, monster = monster_info
        return MonsterRef(
            original_monster_name=original_monster_name,
            template=template,
            variant=variant,
            monster=monster,
            species=species,
        )

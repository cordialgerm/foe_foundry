from __future__ import annotations

from dataclasses import dataclass, replace
from typing import TypeAlias

import inflect

from foe_foundry.creatures import (
    AllSpecies,
    AllTemplates,
    CreatureSpecies,
    Monster,
    MonsterTemplate,
    MonsterVariant,
)
from foe_foundry.utils import name_to_key

p = inflect.engine()

MonsterInfo: TypeAlias = tuple[MonsterTemplate, MonsterVariant | None, Monster | None]


@dataclass(kw_only=True, frozen=True)
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


class MonsterRefResolver:
    """Resolves a monster name to a template, variant, and suggested CR."""

    def __init__(self):
        lookup: dict[str, MonsterInfo] = {}
        alias_lookup: dict[str, MonsterInfo] = {}
        species_lookup: dict[str, CreatureSpecies] = {s.key: s for s in AllSpecies}

        for template in AllTemplates:
            lookup[template.key] = (template, None, None)
            for variant in template.variants:
                for monster in variant.monsters:
                    lookup[monster.key] = (template, variant, monster)

                    if monster.srd_creatures is not None:
                        for alias in monster.srd_creatures:
                            alias_lookup[name_to_key(alias)] = (
                                template,
                                variant,
                                monster,
                            )

                    if monster.other_creatures is not None:
                        for other_creature, _ in monster.other_creatures.items():
                            alias_lookup[name_to_key(other_creature)] = (
                                template,
                                variant,
                                monster,
                            )

        self.lookup = lookup
        self.aliases = alias_lookup
        self.species_lookup = species_lookup

    def resolve_monster_ref(self, monster_name: str) -> MonsterRef | None:
        """Resolves a monster name to a template, variant, and suggested CR."""

        original_monster_name = monster_name

        ref = self._resolve_monster_ref_inner(original_monster_name, monster_name)
        if ref is not None:
            return ref

        singular = p.singular_noun(monster_name)  # type: ignore
        if singular:
            monster_name = singular

        return self._resolve_monster_ref_inner(original_monster_name, monster_name)

    def _resolve_species_from_monster_name(
        self, monster_name: str
    ) -> tuple[CreatureSpecies | None, str | None]:
        """Check if the monster name starts with a species name, like an Orc Berserker"""

        seperators = [" ", "-", "_"]
        if not any(sep in monster_name for sep in seperators):
            return None, None

        for sep in seperators:
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
        original_monster_name: str,
        monster_name: str,
        species_key: str | None = None,
    ) -> MonsterRef | None:
        """Resolves a monster name to a template, variant, and suggested CR."""

        monster_name = monster_name.strip().lower()
        key = name_to_key(monster_name)
        species = self.species_lookup.get(species_key) if species_key else None

        if (monster_info := self.lookup.get(key)) is not None:
            template, variant, monster = monster_info
            return MonsterRef(
                original_monster_name=original_monster_name,
                template=template,
                variant=variant,
                monster=monster,
                species=species,
            )
        elif (monster_info := self.aliases.get(key)) is not None:
            template, variant, monster = monster_info
            return MonsterRef(
                original_monster_name=original_monster_name,
                template=template,
                variant=variant,
                monster=monster,
                species=species,
            )
        else:
            species, rest_of_name = self._resolve_species_from_monster_name(
                monster_name
            )
            if species is None or rest_of_name is None:
                return None
            return self._resolve_monster_ref_inner(
                original_monster_name=original_monster_name,
                monster_name=rest_of_name,
                species_key=species.key if species else None,
            )

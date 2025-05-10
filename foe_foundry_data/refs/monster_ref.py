from __future__ import annotations

from dataclasses import dataclass, replace
from typing import TypeAlias

import inflect

from foe_foundry.creatures import (
    AllTemplates,
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

    def _resolve_monster_ref_inner(
        self, original_monster_name: str, monster_name: str
    ) -> MonsterRef | None:
        """Resolves a monster name to a template, variant, and suggested CR."""

        key = name_to_key(monster_name)
        if (monster_info := self.lookup.get(key)) is not None:
            template, variant, monster = monster_info
            return MonsterRef(
                original_monster_name=original_monster_name,
                template=template,
                variant=variant,
                monster=monster,
            )
        elif (monster_info := self.aliases.get(key)) is not None:
            template, variant, monster = monster_info
            return MonsterRef(
                original_monster_name=original_monster_name,
                template=template,
                variant=variant,
                monster=monster,
            )
        else:
            return None

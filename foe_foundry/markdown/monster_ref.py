from __future__ import annotations

from dataclasses import dataclass, replace

import inflect

from foe_foundry.creatures import (
    AllTemplates,
    CreatureTemplate,
    CreatureVariant,
    SuggestedCr,
)
from foe_foundry.utils import name_to_key

p = inflect.engine()


@dataclass(kw_only=True)
class MonsterRef:
    """A reference to a monster template or variant."""

    original_monster_name: str
    template: CreatureTemplate
    variant: CreatureVariant | None = None
    suggested_cr: SuggestedCr | None = None

    def resolve(self) -> MonsterRef:
        if self.variant is not None:
            return self

        variant = self.template.variants[0]
        suggested_cr = variant.suggested_crs[0]
        return replace(self, variant=variant, suggested_cr=suggested_cr)


class MonsterRefResolver:
    """Resolves a monster name to a template, variant, and suggested CR."""

    def __init__(self):
        lookup: dict[
            str, tuple[CreatureTemplate, CreatureVariant | None, SuggestedCr | None]
        ] = {}

        for template in AllTemplates:
            lookup[template.key] = (template, None, None)
            for variant in template.variants:
                for suggested_cr in variant.suggested_crs:
                    lookup[suggested_cr.key] = (template, variant, suggested_cr)

        self.lookup = lookup

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
        monster_info = self.lookup.get(key)
        if monster_info is not None:
            template, variant, suggested_cr = monster_info
            return MonsterRef(
                original_monster_name=original_monster_name,
                template=template,
                variant=variant,
                suggested_cr=suggested_cr,
            )

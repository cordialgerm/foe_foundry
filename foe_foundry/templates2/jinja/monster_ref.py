from abc import ABC, abstractmethod

import inflect
from markupsafe import Markup

from foe_foundry.creatures import (
    AllTemplates,
    CreatureTemplate,
    CreatureVariant,
    SuggestedCr,
)
from foe_foundry.utils import name_to_key

p = inflect.engine()


class MonsterRefResolver(ABC):
    @abstractmethod
    def resolve_monster_ref(self, monster_name: str) -> Markup | None:
        pass


class TestMonsterRefResolver(MonsterRefResolver):
    def __init__(self):
        lookup: dict[str, tuple[CreatureTemplate, CreatureVariant, SuggestedCr]] = {}

        for template in AllTemplates:
            for variant in template.variants:
                for suggested_cr in variant.suggested_crs:
                    lookup[suggested_cr.key] = (template, variant, suggested_cr)

        self.lookup = lookup

    def resolve_monster_ref(self, monster_name: str) -> Markup | None:
        original_monster_name = monster_name

        singular = p.singular_noun(monster_name)  # type: ignore
        if singular:
            monster_name = singular

        key = name_to_key(monster_name)
        monster_info = self.lookup.get(key)
        if monster_info is not None:
            template, variant, suggested_cr = monster_info
            href = f"{template.key}.html"
            return Markup(
                f"<a href='{href}' class='monster-link' data-monster-template='{template.key}' data-monster-variant='{variant.key}' data-monster='{suggested_cr.key}'><strong>{original_monster_name}</strong></a>"
            )
        else:
            return None

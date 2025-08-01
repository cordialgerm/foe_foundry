from __future__ import annotations

from dataclasses import asdict
from typing import Annotated

import numpy as np
from fastapi import APIRouter, HTTPException, Query
from pydantic.dataclasses import dataclass

from foe_foundry.creatures import AllTemplates
from foe_foundry_data.monsters import MonsterModel, PowerLoadoutModel
from foe_foundry_data.monsters.all import Monsters
from foe_foundry_data.refs import MonsterRefResolver

from .data import MonsterMeta

router = APIRouter(prefix="/api/v1/monsters")
ref_resolver = MonsterRefResolver()


@dataclass(kw_only=True)
class MonsterWithRelations(MonsterModel):
    """
    This model extends the base MonsterModel to include related monster templates.
    It is used to provide additional context when fetching monster data.
    """

    previous_template: MonsterMeta
    next_template: MonsterMeta


def add_relations(monster: MonsterModel) -> MonsterWithRelations:
    """
    Adds previous and next template relations to the monster model.
    """
    template_key = monster.template_key
    ordered_templates = [
        t for t in AllTemplates if t.key == template_key or t.lore_md is not None
    ]
    template_index = next(
        (i for i, t in enumerate(ordered_templates) if t.key == template_key), None
    )
    if template_index is None:
        raise ValueError(f"Template with key {template_key} not found in AllTemplates")

    next_template_index = (
        template_index + 1 if template_index + 1 < len(ordered_templates) else 0
    )
    previous_template_index = (
        template_index - 1 if template_index > 0 else len(ordered_templates) - 1
    )

    next_template = ordered_templates[next_template_index]
    next_monster = next(m for m in next_template.monsters)
    previous_template = ordered_templates[previous_template_index]
    previous_monster = next(m for m in previous_template.monsters)

    return MonsterWithRelations(
        **asdict(monster),
        previous_template=MonsterMeta(
            monster_key=previous_monster.key,
            template_key=previous_template.key,
        ),
        next_template=MonsterMeta(
            monster_key=next_monster.key,
            template_key=next_template.key,
        ),
    )


@router.get("/new")
def new_monsters(
    limit: Annotated[int | None, Query(title="How many new monsters to return")] = None,
) -> list[MonsterMeta]:
    """
    Returns a list of top N new monsters that have been added recently
    """
    if limit is None:
        limit = 5

    created_at = np.array(
        [m.create_date for m in Monsters.one_of_each_monster if m.create_date]
    )
    indexes = np.argsort(created_at)[-1 * limit :][
        ::-1
    ]  # Get the last N created monsters
    monsters = [Monsters.one_of_each_monster[i] for i in indexes]
    return [
        MonsterMeta(monster_key=m.key, template_key=m.template_key) for m in monsters
    ]


@router.get("/{template_or_variant_key}")
def get_template(template_or_variant_key: str) -> MonsterWithRelations:
    ref = ref_resolver.resolve_monster_ref(template_or_variant_key)
    if ref is None:
        raise HTTPException(status_code=404, detail="Template not found")

    ref = ref.resolve()
    monster_key = ref.monster.key  # type: ignore
    monster = Monsters.lookup.get(monster_key)
    if monster is None:
        raise HTTPException(status_code=404, detail="Template not found")

    return add_relations(monster)


@router.get("/{template_or_variant_key}/loadouts")
def get_loadout(template_or_variant_key: str) -> list[PowerLoadoutModel]:
    ref = ref_resolver.resolve_monster_ref(template_or_variant_key)
    if ref is None:
        raise HTTPException(status_code=404, detail="Monster not found")

    ref = ref.resolve()

    settings = ref.template._settings_for_variant(
        variant=ref.variant,  # type: ignore
        monster=ref.monster,  # type: ignore
        species=ref.species,  # type: ignore
    )

    power_selection = ref.template.choose_powers(settings=settings)
    loadouts = power_selection.loadouts
    return [PowerLoadoutModel.from_loadout(loadout) for loadout in loadouts]

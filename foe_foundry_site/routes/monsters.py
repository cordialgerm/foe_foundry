from __future__ import annotations

from dataclasses import asdict
from typing import Annotated

import numpy as np
from fastapi import APIRouter, HTTPException, Query
from pydantic.dataclasses import dataclass

from foe_foundry.creatures import AllTemplates
from foe_foundry_data.base import MonsterInfoModel
from foe_foundry_data.monster_families import MonsterFamilies
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


@dataclass(kw_only=True)
class MonsterGroup:
    name: str
    url: str
    monsters: list[MonsterInfoModel]


@dataclass(kw_only=True)
class SimilarMonsters:
    similar_monsters: list[MonsterGroup]


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
def get_new_monsters(
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


@router.get("/families")
def get_all_families() -> list[dict]:
    """
    Returns a list of all monster families with basic metadata
    """
    try:
        families = MonsterFamilies.families
        return [
            {
                "key": family.key,
                "name": family.name,
                "tag_line": family.tag_line,
                "icon": family.icon,
                "monster_count": len(family.monsters),
                "url": f"/families/{family.key}/"
            }
            for family in families
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading families data: {str(e)}")


@router.get("/family/{family_key}")
def get_monsters_by_family(family_key: str) -> list[MonsterInfoModel]:
    """
    Returns a list of monsters that belong to the specified family
    """
    try:
        families = MonsterFamilies.families
        family = next((f for f in families if f.key == family_key), None)
        if family is None:
            raise HTTPException(status_code=404, detail=f"Family '{family_key}' not found")
        
        return family.monsters
    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(status_code=500, detail=f"Error loading family data: {str(e)}")


@router.get("/{template_or_variant_key}")
def get_monster(template_or_variant_key: str) -> MonsterWithRelations:
    ref = ref_resolver.resolve_monster_ref(template_or_variant_key)
    if ref is None:
        raise HTTPException(status_code=404, detail="Template not found")

    ref = ref.resolve()
    monster_key = ref.monster.key  # type: ignore
    monster = Monsters.lookup.get(monster_key)
    if monster is None:
        raise HTTPException(status_code=404, detail="Template not found")

    return add_relations(monster)


@router.get("/{template_or_variant_key}/similar")
def get_similiar_monsters(template_or_variant_key: str) -> SimilarMonsters:
    ref = ref_resolver.resolve_monster_ref(template_or_variant_key)
    if ref is None:
        raise HTTPException(status_code=404, detail="Template not found")

    ref = ref.resolve()
    monster_key = ref.monster.key  # type: ignore
    monster = Monsters.lookup.get(monster_key)
    if monster is None:
        raise HTTPException(status_code=404, detail="Template not found")

    # Group related monsters by template
    template_groups = {}
    for related_monster in monster.related_monsters:
        template_name = related_monster.template
        if template_name not in template_groups:
            template_groups[template_name] = []
        template_groups[template_name].append(related_monster)

    # Create groups with metadata
    groups = []
    current_monster_cr = monster.cr

    for template_name, monsters in template_groups.items():
        # Sort monsters within group by CR
        sorted_monsters = sorted(monsters, key=lambda m: m.cr)

        # Calculate group CR (lowest CR in the group)
        group_cr = sorted_monsters[0].cr

        # Calculate CR difference from current monster
        cr_difference = abs(current_monster_cr - group_cr)

        # Check if this is the same template as the current monster
        is_same_template = any(m.same_template for m in monsters)

        # Convert MonsterModel to MonsterInfoModel for the response
        monster_info_list = [
            MonsterInfoModel(key=m.key, name=m.name, cr=m.cr, template=m.template)
            for m in sorted_monsters
        ]

        groups.append(
            {
                "template_name": template_name,
                "monsters": monster_info_list,
                "group_cr": group_cr,
                "cr_difference": cr_difference,
                "is_same_template": is_same_template,
            }
        )

    # Sort groups: same template first, then by CR difference
    groups.sort(key=lambda g: (not g["is_same_template"], g["cr_difference"]))

    # Convert to the expected response format
    monster_groups = []
    for group in groups:
        # Create URL for the template (assuming it follows the pattern)
        template_url = f"/monsters/{group['template_name'].lower().replace(' ', '-')}/"

        monster_groups.append(
            MonsterGroup(
                name=group["template_name"],
                url=template_url,
                monsters=group["monsters"],
            )
        )

    return SimilarMonsters(similar_monsters=monster_groups)


@router.get("/{template_or_variant_key}/loadouts")
def get_monster_loadout(template_or_variant_key: str) -> list[PowerLoadoutModel]:
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

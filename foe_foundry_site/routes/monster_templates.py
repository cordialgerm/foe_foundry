from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, HTTPException, Query
from pydantic.dataclasses import dataclass

from foe_foundry.creatures import AllTemplates
from foe_foundry_data.base import MonsterInfoModel, MonsterTemplateInfoModel
from foe_foundry_data.families import load_families
from foe_foundry_data.homepage import load_homepage_data
from foe_foundry_data.monsters.all import Monsters
from foe_foundry_search.search import search_monsters

router = APIRouter(prefix="/api/v1/monster_templates")


@dataclass(kw_only=True)
class MonsterTemplateSearchRequest:
    query: str
    limit: int | None = None


def _get_monster_template(template_key: str) -> MonsterTemplateInfoModel | None:
    """
    Helper function to get the template information for a monster
    """
    homepage_data = load_homepage_data()
    homepage_templates = {m.key: m for m in homepage_data.monsters}
    # Find the template object to get the proper name
    template_obj = homepage_templates.get(template_key)
    if template_obj is None:
        return None

    return MonsterTemplateInfoModel(
        key=template_obj.template,
        name=template_obj.name,
        url=template_obj.url,
        image=template_obj.image,
        tagline=template_obj.tagline,
        transparent_edges=template_obj.transparent_edges,
        grayscale=template_obj.grayscale,
        background_color=template_obj.background_color,
        mask_css=template_obj.mask_css,
        is_new=template_obj.is_new,
        create_date=template_obj.create_date,
    )


def get_distinct_templates_from_monsters(
    monsters: list[MonsterInfoModel],
) -> list[MonsterTemplateInfoModel]:
    """Extract distinct templates from a list of monsters"""
    seen_templates = set()
    templates = []

    for monster in monsters:
        if monster.template not in seen_templates:
            seen_templates.add(monster.template)
            template = _get_monster_template(monster.template)
            if template:
                templates.append(template)

    return templates


@router.get("/new")
def get_new_monster_templates(
    limit: Annotated[
        int | None, Query(title="How many new monster templates to return")
    ] = None,
) -> list[MonsterTemplateInfoModel]:
    """
    Returns a list of top N new monster templates that have been added recently
    """
    if limit is None:
        limit = 5

    # Get templates with create dates, sorted by most recent
    templates_with_dates = [
        (t, t.create_date)
        for t in AllTemplates
        if t.create_date and t.lore_md is not None
    ]

    # Sort by create date descending and take the limit
    sorted_templates = sorted(templates_with_dates, key=lambda x: x[1], reverse=True)
    recent_templates = sorted_templates[:limit]
    templates = [
        _get_monster_template(template.key) for template, _ in recent_templates
    ]
    return [t for t in templates if t is not None]


@router.get("/family/{family_key}")
def get_monster_templates_by_family(family_key: str) -> list[MonsterTemplateInfoModel]:
    """
    Returns a list of monster templates that belong to the specified family
    """
    try:
        families = load_families()
        family = next((f for f in families if f.key == family_key), None)
        if family is None:
            raise HTTPException(
                status_code=404, detail=f"Family '{family_key}' not found"
            )

        # Get distinct templates from the family's monsters
        return get_distinct_templates_from_monsters(family.monsters)

    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(
            status_code=500, detail=f"Error loading family data: {str(e)}"
        )


@router.get("/{template_key}")
def get_monster_template(template_key: str) -> MonsterTemplateInfoModel:
    """
    Returns information about a specific monster template
    """
    template = next((t for t in AllTemplates if t.key == template_key), None)
    if template is None:
        raise HTTPException(
            status_code=404, detail=f"Template '{template_key}' not found"
        )

    template = _get_monster_template(template.key)
    if template is None:
        raise HTTPException(
            status_code=404, detail=f"Template '{template_key}' not found"
        )
    return template


@router.get("/search/")
def get_search_monster_templates(
    query: Annotated[str, Query(title="Search query for monster templates")],
    limit: Annotated[
        int | None, Query(title="How many search results to return")
    ] = None,
) -> list[MonsterTemplateInfoModel]:
    """
    Returns a list of top N monster templates that match the search criteria
    """
    if limit is None:
        limit = 5

    # Search for monsters first, then extract distinct templates
    monster_results = []
    for search_result in search_monsters(
        search_query=query, limit=limit * 10, max_hops=4
    ):
        monster_key = search_result.monster_key
        if not monster_key:
            continue

        monster = Monsters.lookup.get(monster_key)
        if not monster:
            continue

        monster_results.append(
            MonsterInfoModel(
                key=monster.key,
                name=monster.name,
                cr=monster.cr,
                template=monster.template_key,
            )
        )

    # Extract distinct templates and limit the results
    templates = get_distinct_templates_from_monsters(monster_results)
    return templates[:limit]


@router.post("/search")
def post_search_monster_templates(
    request: MonsterTemplateSearchRequest,
) -> list[MonsterTemplateInfoModel]:
    """
    Returns a list of top N monster templates that match the search criteria
    """
    limit = request.limit if request.limit is not None else 5

    # Validate limit parameter
    if limit <= 0:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid limit value: {limit}. Limit must be greater than 0.",
        )

    # Search for monsters first, then extract distinct templates
    monster_results = []
    for search_result in search_monsters(
        search_query=request.query,
        limit=limit * 10,  # Get more monsters to increase chance of distinct templates
        max_hops=4,
    ):
        monster_key = search_result.monster_key
        if not monster_key:
            continue

        monster = Monsters.lookup.get(monster_key)
        if not monster:
            continue

        monster_results.append(
            MonsterInfoModel(
                key=monster.key,
                name=monster.name,
                cr=monster.cr,
                template=monster.template_key,
            )
        )

    # Extract distinct templates and limit the results
    templates = get_distinct_templates_from_monsters(monster_results)
    return templates[:limit]

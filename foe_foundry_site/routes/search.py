from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from foe_foundry.creature_types import CreatureType
from foe_foundry_data.base import MonsterInfoModel
from foe_foundry_data.monsters.all import Monsters
from foe_foundry_search.search import search_monsters

router = APIRouter(prefix="/api/v1/search")


class MonsterSearchRequest(BaseModel):
    query: str
    limit: int | None = None
    target_cr: float | None = None
    creature_types: list[str] | None = None


@router.get("/monsters")
def get_search_monsters(
    query: Annotated[str, Query(title="Search query for monsters")],
    limit: Annotated[
        int | None, Query(title="How many search results to return")
    ] = None,
) -> list[MonsterInfoModel]:
    """
    Returns a list of top N monsters that match the search criteria
    """
    if limit is None:
        limit = 5

    results = []
    for search_result in search_monsters(search_query=query, limit=limit, max_hops=4):
        monster_key = search_result.monster_key
        if not monster_key:
            continue

        monster = Monsters.lookup.get(monster_key)
        if not monster:
            continue

        results.append(
            MonsterInfoModel(
                key=monster.key,
                name=monster.name,
                cr=monster.cr,
                template=monster.template_key,
                background_image=monster.background_image,
                creature_type=monster.creature_type,
                tag_line=monster.tag_line,
            )
        )
    return results


@router.post("/monsters")
def post_search_monsters(request: MonsterSearchRequest) -> list[MonsterInfoModel]:
    """
    Returns a list of top N monsters that match the search criteria
    """
    limit = request.limit if request.limit is not None else 5

    # Validate limit parameter
    if limit <= 0:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid limit value: {limit}. Limit must be greater than 0.",
        )

    # Parse creature types if provided
    creature_types = None
    if request.creature_types:
        creature_types = set()
        for ct_str in request.creature_types:
            try:
                creature_types.add(CreatureType.parse(ct_str))
            except ValueError:
                # Skip invalid creature types
                continue

    results = []
    for search_result in search_monsters(
        search_query=request.query,
        limit=limit,
        target_cr=request.target_cr,
        creature_types=creature_types,
        max_hops=4,
    ):
        monster_key = search_result.monster_key
        if not monster_key:
            continue

        monster = Monsters.lookup.get(monster_key)
        if not monster:
            continue

        results.append(
            MonsterInfoModel(
                key=monster.key,
                name=monster.name,
                cr=monster.cr,
                template=monster.template_key,
                background_image=monster.background_image,
                creature_type=monster.creature_type,
                tag_line=monster.tag_line,
            )
        )
    return results

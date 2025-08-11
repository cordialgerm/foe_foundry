from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Query

from foe_foundry_data.base import MonsterInfoModel
from foe_foundry_data.monsters.all import Monsters
from foe_foundry_search.search import search_monsters

router = APIRouter(prefix="/api/v1/search")


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
            )
        )
    return results

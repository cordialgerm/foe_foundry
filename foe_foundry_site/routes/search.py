from __future__ import annotations

import collections
from pathlib import Path
from typing import Annotated

import yaml
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from foe_foundry.creature_types import CreatureType
from foe_foundry_data.base import MonsterInfoModel
from foe_foundry_data.monsters.all import Monsters
from foe_foundry_search.search import enhanced_search_monsters

router = APIRouter(prefix="/api/v1/search")


class MonsterSearchRequest(BaseModel):
    query: str
    limit: int | None = None
    target_cr: float | None = None
    min_cr: float | None = None
    max_cr: float | None = None
    creature_types: list[str] | None = None


class SearchFacet(BaseModel):
    value: str
    count: int


class SearchFacets(BaseModel):
    creatureTypes: list[SearchFacet]
    crRange: dict[str, float]  # {"min": float, "max": float}


class SearchSeed(BaseModel):
    term: str
    description: str
    examples: list[str] | None = None


class MonsterSearchResult(BaseModel):
    monsters: list[MonsterInfoModel]
    facets: SearchFacets
    total: int | None = None


def _calculate_facets(monsters: list[MonsterInfoModel]) -> SearchFacets:
    """Calculate facets from a list of monsters"""
    # Count creature types
    creature_type_counts = collections.Counter(
        m.creature_type for m in monsters if m.creature_type
    )

    # Create creature type facets, sorted by count descending
    creature_type_facets = [
        SearchFacet(value=creature_type, count=count)
        for creature_type, count in creature_type_counts.most_common()
    ]

    # Calculate CR range
    crs = [m.cr for m in monsters]
    cr_range = {"min": min(crs) if crs else 0.0, "max": max(crs) if crs else 30.0}

    return SearchFacets(creatureTypes=creature_type_facets, crRange=cr_range)


def _get_all_monsters() -> list[MonsterInfoModel]:
    """Get all monsters as MonsterInfoModel objects"""
    all_monsters = Monsters.one_of_each_monster
    return [
        MonsterInfoModel(
            key=monster.key,
            name=monster.name,
            cr=monster.cr,
            template=monster.template_key,
            background_image=monster.background_image,
            creature_type=monster.creature_type,
            tag_line=monster.tag_line,
            tags=monster.tags,
        )
        for monster in all_monsters
    ]


def _load_search_seeds() -> list[SearchSeed]:
    """Load search seeds from the YAML file"""
    seeds_file = Path(__file__).parent.parent.parent / "data" / "search_seeds.yaml"
    try:
        with open(seeds_file, "r") as f:
            data = yaml.safe_load(f)
        return [SearchSeed(**seed) for seed in data.get("search_seeds", [])]
    except Exception:
        # Return empty list if file not found or parse error
        return []


@router.get("/facets")
def get_search_facets() -> SearchFacets:
    """
    Returns available search facets with counts across the entire monster database.
    Used for initial page load to populate filter options.
    """
    all_monsters = _get_all_monsters()
    return _calculate_facets(all_monsters)


@router.get("/seeds")
def get_search_seeds() -> list[SearchSeed]:
    """
    Returns predefined search seed terms to inspire users and help them discover monsters.
    These are curated search terms that are guaranteed to return good results.
    """
    return _load_search_seeds()


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
    for search_result in enhanced_search_monsters(
        search_query=query, limit=limit, max_hops=4
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
                tags=monster.tags,
            )
        )
    return results


@router.post("/monsters")
def post_search_monsters(request: MonsterSearchRequest) -> list[MonsterInfoModel]:
    """
    Returns a list of top N monsters that match the search criteria (backward compatibility)
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

    # Use min_cr/max_cr if provided, otherwise fall back to target_cr
    search_kwargs = {
        "search_query": request.query,
        "limit": limit,
        "creature_types": creature_types,
        "max_hops": 4,
    }
    if request.min_cr is not None or request.max_cr is not None:
        search_kwargs["min_cr"] = request.min_cr
        search_kwargs["max_cr"] = request.max_cr
    else:
        search_kwargs["target_cr"] = request.target_cr

    results = []
    for search_result in enhanced_search_monsters(**search_kwargs):
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
                tags=monster.tags,
            )
        )
    return results


@router.post("/monsters/enhanced")
def post_search_monsters_enhanced(request: MonsterSearchRequest) -> MonsterSearchResult:
    """
    Enhanced search endpoint that returns monsters with facets based on the full database
    """
    limit = request.limit if request.limit is not None else 50

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

    # Use min_cr/max_cr if provided, otherwise fall back to target_cr
    search_kwargs = {
        "search_query": request.query,
        "limit": limit,
        "creature_types": creature_types,
        "max_hops": 4,
    }
    if request.min_cr is not None or request.max_cr is not None:
        search_kwargs["min_cr"] = request.min_cr
        search_kwargs["max_cr"] = request.max_cr
    else:
        search_kwargs["target_cr"] = request.target_cr

    results = []
    for search_result in enhanced_search_monsters(**search_kwargs):
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
                tags=monster.tags,
            )
        )

    # Always return facets based on the full database, not just search results
    # This ensures all filter options remain visible with their full counts
    all_monsters = _get_all_monsters()
    facets = _calculate_facets(all_monsters)

    return MonsterSearchResult(monsters=results, facets=facets, total=len(results))

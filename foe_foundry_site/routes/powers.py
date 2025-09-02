from datetime import datetime
from typing import Annotated

import numpy as np
from fastapi import APIRouter, HTTPException, Query

from foe_foundry import CreatureType, MonsterRole
from foe_foundry.utils import name_to_key
from foe_foundry_data.powers import PowerModel, Powers
from foe_foundry_search.search import search_powers as search_powers_core

router = APIRouter(prefix="/api/v1/powers")


@router.get("/power/{power_name}")
def get_power(*, power_name: str) -> PowerModel:
    key = name_to_key(power_name)
    power = Powers.PowerLookup.get(key)
    if power is None:
        raise HTTPException(status_code=404, detail="Power not found")
    return power


@router.get("/random")
def random(
    *,
    limit: Annotated[
        int | None, Query(title="maximum response size", ge=1, le=20)
    ] = 10,
) -> list[PowerModel]:
    limit = limit or 10
    rng = np.random.default_rng()

    keys = list(Powers.PowerLookup.keys())
    indexes = rng.choice(len(keys), size=limit, replace=False)
    powers = [Powers.PowerLookup[keys[i]] for i in indexes]
    return powers


@router.get("/new")
def new(
    *,
    limit: Annotated[
        int | None, Query(title="maximum response size", ge=1, le=20)
    ] = 10,
) -> list[PowerModel]:
    limit = limit or 10

    def _sort(p: PowerModel):
        return p.create_date or datetime.min

    sorted_powers = sorted(Powers.AllPowers, key=_sort, reverse=True)
    return sorted_powers[:limit]


@router.get("/search")
def search_powers(
    *,
    keyword: Annotated[
        str | None, Query(title="search for powers containing this keyword")
    ] = None,
    creature_type: Annotated[
        CreatureType | None,
        Query(title="filter results to a specific creature type"),
    ] = None,
    role: Annotated[
        MonsterRole | None, Query(title="filter results to a specific role")
    ] = None,
    theme: Annotated[
        str | None, Query(title="filter results to a specific theme")
    ] = None,
    limit: Annotated[
        int | None, Query(title="maximum response size", ge=1, le=40)
    ] = 20,
) -> list[PowerModel]:
    limit = limit or 10

    # pre-processing
    keyword = keyword.lower().strip() if keyword is not None else None

    # if the keyword matches a creature type exactly then don't do full text search
    # instead, filter by creature type
    if keyword is not None and creature_type is None:
        try:
            creature_type = CreatureType(keyword)
            keyword = None
        except ValueError:
            pass

    # if the keyword matches a role exactly then don't do full text search
    # instead, filter by role
    if keyword is not None and role is None:
        try:
            role = MonsterRole(keyword)
            keyword = None
        except ValueError:
            pass

    # if the keyword matches a theme exactly then don't do a full text search
    # instead, filter by theme
    if keyword is not None and keyword in Powers.Themes:
        try:
            theme = keyword
            keyword = None
        except ValueError:
            pass

    # if a specific filter is requested we don't really need a limit
    # this is because we don't have to do a full text search
    if keyword is None and (creature_type or role or theme):
        limit = 100

    if keyword:
        powers = []
        for result in search_powers_core(keyword, limit=limit):
            if not result.power_key:
                continue

            power = Powers.PowerLookup.get(result.power_key)
            if power is not None:
                powers.append(power)

    else:
        powers = Powers.PowerLookup.values()

    def check_creature_type(p: PowerModel) -> bool:
        if not creature_type:
            return True
        return creature_type.lower() == p.theme.lower()

    def check_role(p: PowerModel) -> bool:
        if not role:
            return True
        return role.lower() == p.theme.lower()

    def check_theme(p: PowerModel) -> bool:
        return not theme or theme == p.theme

    results = []
    for power in powers:
        if len(results) >= limit:
            break

        if check_creature_type(power) and check_role(power) and check_theme(power):
            results.append(power)

    return results

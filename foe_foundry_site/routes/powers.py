from datetime import datetime, timedelta, timezone
from typing import Annotated

import numpy as np
from fastapi import APIRouter, HTTPException, Query

from foe_foundry import CreatureType, MonsterRole
from foe_foundry.powers import Power

from ..data.power import PowerModel
from . import whoosh

# note - lifespan doesn't work on APIRouter currently
router = APIRouter(prefix="/api/v1/powers")


@router.get("/power/{power_name}")
def get_power(*, power_name: str) -> PowerModel:
    key = Power.name_to_key(power_name)
    power = whoosh.PowerLookup.get(key)
    if power is None:
        raise HTTPException(status_code=404, detail="Power not found")
    return power


@router.get("/random")
def random(
    *, limit: Annotated[int | None, Query(title="maximum response size", ge=1, le=20)] = 10
) -> list[PowerModel]:
    limit = limit or 10
    rng = np.random.default_rng()
    keys = list(whoosh.PowerLookup.keys())
    indexes = rng.choice(len(keys), size=limit, replace=False)
    powers = [whoosh.PowerLookup[keys[i]] for i in indexes]
    return powers


@router.get("/new")
def new(
    *, limit: Annotated[int | None, Query(title="maximum response size", ge=1, le=20)] = 10
) -> list[PowerModel]:
    limit = limit or 10
    now = datetime.now()
    new = now - timedelta(days=30)
    new_powers = [
        p
        for p in whoosh.PowerLookup.values()
        if (p.create_date is not None and p.create_date >= new)
    ]
    sorted_powers = sorted(new_powers, key=lambda x: x.create_date, reverse=True)
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
    theme: Annotated[str | None, Query(title="filter results to a specific theme")] = None,
    limit: Annotated[int | None, Query(title="maximum response size", ge=1, le=40)] = 20,
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
    if keyword is not None and keyword in whoosh.Themes:
        try:
            theme = keyword
            keyword = None
        except ValueError:
            pass

    # if a specific filter is requested we don't really need a limit
    # this is because we don't have to do a full text search
    if creature_type or role or theme:
        limit = 100

    if keyword:
        powers = whoosh.search(keyword, limit=limit)
    else:
        powers = whoosh.PowerLookup.values()

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

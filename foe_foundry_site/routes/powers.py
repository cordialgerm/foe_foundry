from typing import Annotated

from fastapi import APIRouter, HTTPException, Query

from foe_foundry import CreatureType, MonsterRole
from foe_foundry.powers import Power

from ..data.power import PowerModel
from . import whoosh

router = APIRouter(prefix="/api/v1/powers")


@router.get("/power/{power_name}")
def get_power(*, power_name: str) -> PowerModel:
    key = Power.name_to_key(power_name)
    power = whoosh.PowerLookup.get(key)
    if power is None:
        raise HTTPException(status_code=404, detail="Power not found")
    return power


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
    limit: Annotated[int | None, Query(title="maximum response size", ge=1, le=20)] = 10,
) -> list[PowerModel]:
    limit = limit or 10

    if keyword:
        powers = whoosh.search(keyword, limit=limit)
    else:
        powers = whoosh.PowerLookup.values()

    def check_creature_type(p: PowerModel) -> bool:
        return not creature_type or creature_type in p.creature_types

    def check_role(p: PowerModel) -> bool:
        return not role or role in p.roles

    results = []
    for power in powers:
        if len(results) >= limit:
            break

        if check_creature_type(power) and check_role(power):
            results.append(power)

    return results

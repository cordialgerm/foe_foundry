from fastapi import APIRouter

from foe_foundry.powers import AllPowers, Power

router = APIRouter(prefix="/api/v1/powers")

_lookup = {power.key: power for power in AllPowers}


@router.get("/power/{power_name}")
def get_power(power_name: str):
    key = Power.name_to_key(power_name)
    _lookup.get(key)
    pass


# TEMP
@router.post("/search")
def search_powers():
    pass

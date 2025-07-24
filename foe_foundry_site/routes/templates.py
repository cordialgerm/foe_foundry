from __future__ import annotations

from fastapi import APIRouter, HTTPException

from foe_foundry_data.monsters import MonsterModel, PowerLoadoutModel
from foe_foundry_data.monsters.all import Monsters
from foe_foundry_data.refs import MonsterRefResolver

router = APIRouter(prefix="/api/v1/templates")
ref_resolver = MonsterRefResolver()


@router.get("/{template_or_variant_key}")
def get_template(template_or_variant_key: str) -> MonsterModel:
    ref = ref_resolver.resolve_monster_ref(template_or_variant_key)
    if ref is None:
        raise HTTPException(status_code=404, detail="Template not found")

    ref = ref.resolve()
    monster_key = ref.monster.key  # type: ignore
    monster = Monsters.lookup.get(monster_key)
    if monster is None:
        raise HTTPException(status_code=404, detail="Template not found")

    return monster


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

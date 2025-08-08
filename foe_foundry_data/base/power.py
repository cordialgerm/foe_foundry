from __future__ import annotations

from typing import List

from pydantic.dataclasses import dataclass

from foe_foundry.powers import Power, PowerLoadout


@dataclass(kw_only=True)
class PowerInfoModel:
    key: str
    name: str
    power_category: str
    source: str
    theme: str
    icon: str

    @staticmethod
    def from_power(power: Power) -> PowerInfoModel:
        return PowerInfoModel(
            key=power.key,
            name=power.name,
            power_category=power.power_category.name,
            source=power.source or "UNKNOWN",
            theme=power.theme or "UNKNOWN",
            icon=power.icon or "",
        )


@dataclass(kw_only=True)
class PowerLoadoutModel:
    key: str
    name: str
    flavor_text: str
    selection_count: int
    locked: bool
    replace_with_species_powers: bool
    powers: List[PowerInfoModel]

    @staticmethod
    def from_loadout(loadout: PowerLoadout):
        return PowerLoadoutModel(
            key=loadout.key,
            name=loadout.name,
            flavor_text=loadout.flavor_text,
            selection_count=loadout.selection_count,
            locked=loadout.locked,
            replace_with_species_powers=loadout.replace_with_species_powers,
            powers=[PowerInfoModel.from_power(power) for power in loadout.powers],
        )

from dataclasses import dataclass

import numpy as np

from ..power import Power


@dataclass
class CustomPowerWeight:
    weight: float
    ignore_usual_requirements: bool = False


class CustomPowerSelection:
    def filter_power(self, power: Power) -> bool:
        if power in self.force_powers():
            return False

        return True

    def custom_weight(self, power: Power) -> CustomPowerWeight:
        return CustomPowerWeight(weight=1.0, ignore_usual_requirements=False)

    def force_powers(self) -> list[Power]:
        return []

    def power_delta(self) -> float:
        return 0.0


@dataclass(kw_only=True, frozen=True)
class PowerLoadout:
    name: str
    flavor_text: str
    powers: list[Power]
    selection_count: int = 1
    locked: bool = False
    replace_with_species_powers: bool = False


class NewPowerSelection(CustomPowerSelection):
    def __init__(self, loadouts: list[PowerLoadout], rng: np.random.Generator):
        self.loadouts = loadouts
        self.rng = rng

        powers: list[Power] = []
        for loadout in loadouts:
            if loadout.selection_count == 0:
                continue
            elif loadout.selection_count == len(loadout.powers):
                powers.extend(loadout.powers)
            else:
                selection_indexes = self.rng.choice(
                    len(loadout.powers), size=loadout.selection_count, replace=False
                )
                powers.extend([loadout.powers[i] for i in selection_indexes])

        self.powers = powers

    def custom_weight(self, power: Power) -> CustomPowerWeight:
        return CustomPowerWeight(weight=0.0, ignore_usual_requirements=False)

    def force_powers(self) -> list[Power]:
        return self.powers

    def power_delta(self) -> float:
        return sum(p.power_level for p in self.powers)

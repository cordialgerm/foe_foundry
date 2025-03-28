from dataclasses import dataclass

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

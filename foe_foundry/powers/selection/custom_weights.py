from dataclasses import dataclass
from typing import Callable, TypeAlias

from ..power import Power


@dataclass
class CustomPowerWeight:
    weight: float
    ignore_usual_requirements: bool = False


CustomWeightCallback: TypeAlias = Callable[[Power], CustomPowerWeight]

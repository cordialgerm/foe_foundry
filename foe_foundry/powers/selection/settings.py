from dataclasses import dataclass, field

import numpy as np


@dataclass(kw_only=True, frozen=True)
class SelectionSettings:
    rng: np.random.Generator
    power_weights: dict[str, float] = field(default_factory=dict)

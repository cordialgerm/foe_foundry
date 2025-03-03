from dataclasses import dataclass, field

from ...utils import name_to_key
from ..power import Power


@dataclass
class SelectionSettings:
    temperature: float = 1.0
    top_k: int = 40
    retries: int = 3
    power_multiplier: float = 1.0

    boost_powers: dict[str, float] = field(default_factory=dict)
    boost_themes: dict[str, float] = field(default_factory=dict)

    def __post_init__(self):
        self.boost_powers = {name_to_key(k): v for k, v in self.boost_powers.items()}
        self.boost_themes = {name_to_key(k): v for k, v in self.boost_themes.items()}

    def get_boost(self, power: Power) -> float:
        b1 = self.boost_powers.get(power.key, 0.0)

        if power.theme_key is not None:
            b2 = self.boost_themes.get(power.theme_key, 0.0)
        else:
            b2 = 0

        return b1 + b2

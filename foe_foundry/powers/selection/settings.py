from dataclasses import dataclass


@dataclass
class SelectionSettings:
    temperature: float = 1.0
    top_k: int = 40
    retries: int = 3
    power_multiplier: float = 1.0

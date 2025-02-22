from __future__ import annotations

from dataclasses import dataclass


@dataclass(kw_only=True)
class SelectionScore:
    score: float
    score_raw: float
    penalties: float

    remaining_power: float

    bonus_over_target: int
    bonus_over_max: int

    reactions_over_target: int
    reactions_over_max: int

    recharges_over_target: int
    recharges_over_max: int

    attack_modifiers_over_target: int
    attack_modifiers_over_max: int

    limited_uses_over_target: int
    limited_uses_over_max: int

    spellcasting_over_target: int
    spellcasting_over_max: int

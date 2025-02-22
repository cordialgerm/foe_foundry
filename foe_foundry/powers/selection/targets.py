from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(kw_only=True)
class SelectionTargets:
    bonus_action_target: int = 1
    bonus_action_max: int = 2

    reaction_target: int = 1
    reaction_max: int = 2

    recharge_target: int = 1
    recharge_max: int = 1

    attack_modifier_target: int = 1
    attack_modifier_max: int = 1

    limited_uses_target: int = 1
    limited_uses_max: int = 2

    spellcasting_powers_target: int = 1
    spellcasting_powers_max: int = 1

    power_level_target: float
    power_level_max: float

    def copy(self, **kwargs) -> SelectionTargets:
        args = asdict(self)
        args.update(kwargs)
        return SelectionTargets(**args)

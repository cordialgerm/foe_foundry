from __future__ import annotations

from dataclasses import asdict, dataclass, field


@dataclass
class MonsterDials:
    hp_multiplier: float = 1.0
    ac_modifier: int = 0
    multiattack_modifier: int = 0
    attack_hit_modifier: int = 0
    attack_damage_multiplier: float = 1.0
    difficulty_class_modifier: int = 0
    recommended_powers_modifier: float = 0
    speed_modifier: int = 0

    def copy(self, **overrides) -> MonsterDials:
        args = asdict(self)
        args.update(overrides)
        return MonsterDials(**args)

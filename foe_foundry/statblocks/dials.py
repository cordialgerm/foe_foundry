from __future__ import annotations

from dataclasses import asdict, dataclass, field

from ..skills import Stats


@dataclass
class MonsterDials:
    hp_multiplier: float = 1.0
    ac_modifier: int = 0
    multiattack_modifier: int = 0
    attack_hit_modifier: int = 0
    attack_damage_dice_modifier: int = 0
    attack_damage_modifier: int = 0
    difficulty_class_modifier: int = 0
    recommended_powers_modifier: int = 0
    speed_modifier: int = 0
    attribute_modifications: dict = field(default_factory=dict)
    primary_attribute_modifier: int = 0
    primary_attribute: Stats | None = None
    attribute_backup_score: int = 10

    def copy(self, **overrides) -> MonsterDials:
        args = asdict(self)
        args.update(overrides)
        return MonsterDials(**args)

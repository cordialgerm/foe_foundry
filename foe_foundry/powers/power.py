from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List

from ..creature_types import CreatureType
from ..damage import AttackType, DamageType
from ..features import Feature
from ..role_types import MonsterRole
from ..statblocks import BaseStatblock
from .power_type import PowerType
from .scoring import score as standard_score

RIBBON_POWER = 0.25
LOW_POWER = 0.5
MEDIUM_POWER = 1
HIGH_POWER = 1.5
EXTRA_HIGH_POWER = 2


class Power(ABC):
    def __init__(
        self,
        name: str,
        power_type: PowerType,
        source: str | None = None,
        power_level: float = MEDIUM_POWER,
        roles: List[MonsterRole] | None = None,
        creature_types: List[CreatureType] | None = None,
        damage_types: List[DamageType] | None = None,
        attack_types: List[AttackType] | None = None,
        suggested_cr: float | None = None,
        create_date: datetime | None = None,
        theme: str | None = None,
    ):
        self.name = name
        self.power_type = power_type
        self.source = source
        self.power_level = power_level
        self.roles = roles
        self.creature_types = creature_types
        self.damage_types = damage_types
        self.attack_types = attack_types
        self.suggested_cr = suggested_cr
        self.create_date = create_date
        self.theme = theme

        if self.power_level == EXTRA_HIGH_POWER:
            self.power_level_text = "Extra High Power"
        elif self.power_level == HIGH_POWER:
            self.power_level_text = "High Power"
        elif self.power_level == MEDIUM_POWER:
            self.power_level_text = "Medium Power"
        elif self.power_level == LOW_POWER:
            self.power_level_text = "Low Power"
        elif self.power_level == RIBBON_POWER:
            self.power_level_text = "Ribbon"
        else:
            raise ValueError(f"Invalid power level {self.power_level}")

    @property
    def key(self) -> str:
        return Power.name_to_key(self.name)

    @abstractmethod
    def score(self, candidate: BaseStatblock, relaxed_mode: bool = False) -> float:
        pass

    def modify_stats(self, stats: BaseStatblock) -> BaseStatblock:
        return stats

    @abstractmethod
    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        pass

    def __repr__(self):
        return f"{self.name} ({self.power_type})"

    def __hash__(self) -> int:
        return hash(self.key)

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Power) and self.key == other.key

    @staticmethod
    def name_to_key(name: str) -> str:
        return name.lower().replace(" ", "-")


class PowerWithStandardScoring(Power):
    def __init__(
        self,
        name: str,
        power_type: PowerType,
        source: str | None = None,
        power_level: float = MEDIUM_POWER,
        create_date: datetime | None = None,
        theme: str | None = None,
        score_args: Dict[str, Any] | None = None,
    ):
        def resolve_arg_list(arg: str) -> List | None:
            if not score_args:
                return None

            val = score_args.get(f"require_{arg}", score_args.get(f"bonus_{arg}"))
            if val is None:
                return None
            elif isinstance(val, list):
                return val
            elif isinstance(val, set):
                return list(val)
            else:
                return [val]

        def resolve_arg(arg: str) -> Any | None:
            if not score_args:
                return None

            return score_args.get(f"require_{arg}", score_args.get(f"bonus_{arg}"))

        creature_types = resolve_arg_list("types")
        damage_types = resolve_arg_list("damage")
        roles = resolve_arg_list("roles")
        suggested_cr = resolve_arg("cr")
        attack_types = resolve_arg_list("attack_types")

        super().__init__(
            name=name,
            power_type=power_type,
            source=source,
            power_level=power_level,
            create_date=create_date,
            theme=theme,
            roles=roles,
            creature_types=creature_types,
            damage_types=damage_types,
            attack_types=attack_types,
            suggested_cr=suggested_cr,
        )

        self.score_args = score_args

    def score(self, candidate: BaseStatblock, relaxed_mode: bool = False) -> float:
        return standard_score(
            candidate=candidate, relaxed_mode=relaxed_mode, **self.score_args or {}
        )

from __future__ import annotations

from enum import StrEnum
from typing import Any, Callable, List, cast


class Stats(StrEnum):
    STR = "STR"
    DEX = "DEX"
    CON = "CON"
    INT = "INT"
    WIS = "WIS"
    CHA = "CHA"

    @staticmethod
    def All() -> List[Stats]:
        return [cast(Stats, s) for s in Stats._member_map_.values()]

    @staticmethod
    def Primary(mod: int = 0) -> Callable:
        class _PrimaryWrapper:
            def __init__(self):
                self.is_primary = True

            def __call__(self, stats: Any) -> int:
                return stats.primary_attribute_score + mod

        return _PrimaryWrapper()

    @staticmethod
    def Boost(stat: Stats, mod: int) -> Callable:
        def f(stats: Any) -> int:
            return stats.attributes.stat(stat) + mod

        return f

    @staticmethod
    def Scale(base: int, cr_multiplier: float) -> Callable:
        def f(stats: Any) -> int:
            new_stat = min(
                int(round(base + cr_multiplier * stats.cr)), stats.primary_attribute_score
            )
            return new_stat

        return f


class Skills(StrEnum):
    Athletics = "Athletics"
    Acrobatics = "Acrobatics"
    SleightOfHand = "SleightOfHand"
    Stealth = "Stealth"
    Arcana = "Arcana"
    History = "History"
    Investigation = "Investigation"
    Nature = "Nature"
    Religion = "Religion"
    AnimalHandling = "AnimalHandling"
    Insight = "Insight"
    Medicine = "Medicine"
    Perception = "Perception"
    Survival = "Survival"
    Deception = "Deception"
    Intimidation = "Intimidation"
    Performance = "Performance"
    Persuasion = "Persuasion"

    @property
    def stat(self) -> Stats:
        map = {
            Skills.Athletics: Stats.STR,
            Skills.Acrobatics: Stats.DEX,
            Skills.SleightOfHand: Stats.DEX,
            Skills.Stealth: Stats.DEX,
            Skills.Arcana: Stats.INT,
            Skills.History: Stats.INT,
            Skills.Investigation: Stats.INT,
            Skills.Nature: Stats.INT,
            Skills.Religion: Stats.INT,
            Skills.AnimalHandling: Stats.WIS,
            Skills.Insight: Stats.WIS,
            Skills.Medicine: Stats.WIS,
            Skills.Perception: Stats.WIS,
            Skills.Survival: Stats.WIS,
            Skills.Deception: Stats.CHA,
            Skills.Intimidation: Stats.CHA,
            Skills.Performance: Stats.CHA,
            Skills.Persuasion: Stats.CHA,
        }
        return map[self]

    @staticmethod
    def All() -> List[Skills]:
        return [cast(Skills, s) for s in Skills._member_map_.values()]

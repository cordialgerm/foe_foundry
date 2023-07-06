from __future__ import annotations

from enum import StrEnum
from typing import List, cast


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

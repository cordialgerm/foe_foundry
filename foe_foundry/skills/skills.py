from __future__ import annotations

from typing import Any, Callable, List, cast

from backports.strenum import StrEnum


class Stats(StrEnum):
    """
    Enum representing the six core ability scores (stats) in D&D 5e.
    Provides utility methods for stat description, selection, and scaling.
    """

    STR = "STR"
    DEX = "DEX"
    CON = "CON"
    INT = "INT"
    WIS = "WIS"
    CHA = "CHA"

    @property
    def description(self) -> str:
        """
        Returns the full name of the stat (e.g., 'Strength' for STR).
        """
        if self == Stats.STR:
            return "Strength"
        elif self == Stats.DEX:
            return "Dexterity"
        elif self == Stats.CON:
            return "Constitution"
        elif self == Stats.INT:
            return "Intelligence"
        elif self == Stats.WIS:
            return "Wisdom"
        elif self == Stats.CHA:
            return "Charisma"
        else:
            raise ValueError(f"Invalid stat: {self}")

    @staticmethod
    def All() -> List[Stats]:
        """
        Returns a list of all Stats enum members.
        """
        return [cast(Stats, s) for s in Stats._member_map_.values()]

    @staticmethod
    def Primary(mod: int = 0) -> Callable:
        """
        Returns a callable that, when given a stats object, returns a stat value appropriate for the primary stat of a creature of the given CR that is passed in, plus an additional modifier.
        Example: `Stats.Primary(mod=2)(stats(cr=4))` would return an ability score that is appropriate for the primary ability of a CR 4 creature with an additional +2 modifier
        """

        class _PrimaryWrapper:
            def __init__(self):
                self.is_primary = True

            def __call__(self, stats: Any) -> int:
                return stats.primary_attribute_score + mod

        return _PrimaryWrapper()

    def Boost(self, mod: int) -> Callable:
        """
        Returns a callable that, when given a stats object, returns the current stat value boosted by mod, but not exceeding the primary attribute score.
        """

        def f(stats: Any) -> int:
            return min(stats.attributes.stat(self) + mod, stats.primary_attribute_score)

        return f

    @staticmethod
    def Scale(base: int, cr_multiplier: float) -> Callable:
        """
        Returns a callable that, when given a stats object, computes a scaled stat value based on a base value,
        a challenge rating multiplier, and the primary attribute score as a cap.
        """

        def f(stats: Any) -> int:
            new_stat = min(
                int(round(base + cr_multiplier * stats.cr)),
                stats.primary_attribute_score,
            )
            return new_stat

        return f

    def scaler(self, scaling: StatScaling, mod: float = 0) -> StatScaler:
        """
        Returns a StatScaler object for this stat, with the given scaling type and modifier.
        """
        return StatScaler(self, scaling, mod)


class StatScaler:
    """
    Helper class for scaling a stat value based on challenge rating (CR) and scaling type.
    """

    def __init__(self, stat: Stats, scaling: StatScaling, mod: float):
        self.stat = stat
        self.scaling = scaling
        self.mod = mod

    def scale(self, cr: float) -> float:
        """
        Returns the scaled stat value for a given challenge rating (CR),
        using the scaling type and modifier provided at initialization.
        """
        if self.scaling == StatScaling.Primary:
            if cr <= 1 / 8:
                return 12 + self.mod
            elif cr <= 1 / 2:
                return 14 + self.mod
            elif cr <= 1:
                return 14.5 + self.mod
            elif cr <= 2:
                return 16 + self.mod
            elif cr <= 4:
                return 18 + self.mod
            elif cr <= 7:
                return 18.5 + self.mod
            elif cr <= 11:
                return 20 + self.mod
            elif cr <= 15:
                return 22 + self.mod
            else:
                return 23 + self.mod
        elif self.scaling == StatScaling.Low:
            if cr <= 1 / 8:
                return 7.5 + self.mod
            elif cr <= 1 / 2:
                return 8 + self.mod
            elif cr <= 1:
                return 8 + self.mod
            elif cr <= 2:
                return 9 + self.mod
            elif cr <= 4:
                return 9 + self.mod
            elif cr <= 7:
                return 9.5 + self.mod
            elif cr <= 11:
                return 10 + self.mod
            elif cr <= 15:
                return 11 + self.mod
            else:
                return 12 + self.mod
        elif self.scaling == StatScaling.Medium:
            if cr <= 1 / 8:
                return 10 + self.mod
            elif cr <= 1 / 2:
                return 10.5 + self.mod
            elif cr <= 1:
                return 11 + self.mod
            elif cr <= 2:
                return 12 + self.mod
            elif cr <= 4:
                return 12.5 + self.mod
            elif cr <= 7:
                return 13.5 + self.mod
            elif cr <= 11:
                return 14.5 + self.mod
            elif cr <= 15:
                return 15.5 + self.mod
            else:
                return 16.5 + self.mod
        elif self.scaling == StatScaling.Constitution:
            if cr <= 1 / 8:
                return 10 + self.mod
            elif cr <= 1 / 2:
                return 12 + self.mod
            elif cr <= 2:
                return 14 + self.mod
            elif cr <= 4:
                return 14 + self.mod
            elif cr <= 7:
                return 14 + self.mod
            elif cr <= 11:
                return 16 + self.mod
            elif cr <= 15:
                return 18 + self.mod
            else:
                return 20 + self.mod
        elif self.scaling == StatScaling.Default:
            if cr <= 4:
                return 10 + self.mod
            else:
                return 12 + self.mod
        elif self.scaling == StatScaling.NoScaling:
            return 10 + self.mod

        raise ValueError(f"Invalid scaling: {self.scaling}")


class StatScaling(StrEnum):
    """
    Enum representing different scaling formulas for stats based on CR.
    """

    Low = "Low"
    Medium = "Medium"
    Default = "Default"
    Primary = "Primary"
    Constitution = "Constitution"
    NoScaling = "NoScaling"  # Used for ability scores that do not scale with CR. For example, a beast's intelligence


class Skills(StrEnum):
    """
    Enum representing all D&D 5e skills, with a mapping to their associated stat.
    """

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
    Initiative = "Initiative"

    @property
    def stat(self) -> Stats:
        """
        Returns the stat associated with this skill (e.g., Athletics -> STR).
        """
        map = {
            Skills.Athletics: Stats.STR,
            Skills.Acrobatics: Stats.DEX,
            Skills.SleightOfHand: Stats.DEX,
            Skills.Initiative: Stats.DEX,
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
        """
        Returns a list of all Skills enum members.
        """
        return [cast(Skills, s) for s in Skills._member_map_.values()]

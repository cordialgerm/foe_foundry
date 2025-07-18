# 5E ability scores and scaling logic for foe_foundry.
# Includes docstrings and comments for context and future maintainers.
from __future__ import annotations

from typing import Any, Callable, List, cast

from backports.strenum import StrEnum


class AbilityScore(StrEnum):
    """
    Enum representing the six 5E ability scores (attributes).
    Each ability score is a core stat that influences skills, saving throws, and combat.
    """

    STR = "STR"  # Strength: Physical power, carrying, melee attacks, athletics
    DEX = "DEX"  # Dexterity: Agility, reflexes, balance, stealth, ranged attacks
    CON = "CON"  # Constitution: Endurance, health, stamina, resisting poison/disease
    INT = "INT"  # Intelligence: Reasoning, memory, knowledge, investigation, magic
    WIS = "WIS"  # Wisdom: Perception, insight, willpower, animal handling, survival
    CHA = "CHA"  # Charisma: Influence, leadership, persuasion, deception, performance

    @property
    def description(self) -> str:
        """
        Returns the full name of the ability score (e.g., 'Strength' for STR).
        """
        if self == AbilityScore.STR:
            return "Strength"
        elif self == AbilityScore.DEX:
            return "Dexterity"
        elif self == AbilityScore.CON:
            return "Constitution"
        elif self == AbilityScore.INT:
            return "Intelligence"
        elif self == AbilityScore.WIS:
            return "Wisdom"
        elif self == AbilityScore.CHA:
            return "Charisma"
        else:
            raise ValueError(f"Invalid stat: {self}")

    @staticmethod
    def All() -> List["AbilityScore"]:
        """
        Returns a list of all AbilityScore enum members.
        Useful for iteration, validation, or UI display.
        """
        return [cast(AbilityScore, s) for s in AbilityScore._member_map_.values()]

    @staticmethod
    def Primary(mod: int = 0) -> Callable:
        """
        Returns a callable that, when given a stats object, returns the primary attribute score plus an optional modifier.
        Used for scaling monster stats based on their primary ability.
        """

        class _PrimaryWrapper:
            def __init__(self):
                self.is_primary = True

            def __call__(self, stats: Any) -> int:
                return stats.primary_attribute_score + mod

        return _PrimaryWrapper()

    def Boost(self, mod: int) -> Callable:
        """
        Returns a callable that boosts this ability score by a modifier, but not above the primary attribute score.
        Used for scaling secondary stats while respecting the primary stat cap.
        """

        def f(stats: Any) -> int:
            return min(stats.attributes.stat(self) + mod, stats.primary_attribute_score)

        return f

    @staticmethod
    def Scale(base: int, cr_multiplier: float) -> Callable:
        """
        Returns a callable that scales a stat based on a base value and a challenge rating multiplier.
        Used for dynamic stat generation for monsters/NPCs.
        """

        def f(stats: Any) -> int:
            new_stat = min(
                int(round(base + cr_multiplier * stats.cr)),
                stats.primary_attribute_score,
            )
            return new_stat

        return f

    def scaler(self, scaling: StatScaling, mod: float = 0) -> "StatScaler":
        """
        Returns a StatScaler object for this ability score, with the given scaling type and modifier.
        Used for advanced stat scaling logic.
        """
        return StatScaler(self, scaling, mod)


class StatScaler:
    """
    Helper class for scaling an ability score based on challenge rating (CR) and scaling type.
    Used to generate monster/NPC stats that scale with difficulty.
    """

    def __init__(self, stat: AbilityScore, scaling: "StatScaling", mod: float):
        self.stat = stat
        self.scaling = scaling
        self.mod = mod

    def scale(self, cr: float) -> float:
        """
        Returns the scaled stat value for a given challenge rating (CR).
        Scaling formulas are based on foe_foundry design guidelines.
        """
        if self.scaling == StatScaling.Primary:
            # Used for a monster's main stat (e.g., STR for a brute)
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
            # Used for a monster's dump stat or weak attribute
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
            # Used for a monster's average stat
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
            # Used for scaling Constitution (HP resilience) specifically
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
            # Used for generic scaling
            if cr <= 4:
                return 10 + self.mod
            else:
                return 12 + self.mod
        elif self.scaling == StatScaling.NoScaling:
            # Used when no scaling is desired
            return 10 + self.mod

        raise ValueError(f"Invalid scaling: {self.scaling}")


class StatScaling(StrEnum):
    """
    Enum for stat scaling types used in foe_foundry monster/NPC generation.
    Determines how an ability score should scale with challenge rating (CR).
    """

    Low = "Low"  # For dump stats or weak attributes
    Medium = "Medium"  # For average stats
    Default = "Default"  # For generic scaling
    Primary = "Primary"  # For a monster's main stat
    Constitution = "Constitution"  # For scaling Constitution specifically
    NoScaling = "NoScaling"  # For static stats (no scaling)

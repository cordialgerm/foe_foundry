from enum import StrEnum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from foe_foundry.skills.ability_scores import AbilityScore


class StatScaler:
    """
    Helper class for scaling an ability score based on challenge rating (CR) and scaling type.
    Used to generate monster/NPC stats that scale with difficulty.
    """

    def __init__(self, stat: "AbilityScore", scaling: "StatScaling", mod: float):
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

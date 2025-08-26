# 5E ability scores and scaling logic for foe_foundry.
# Includes docstrings and comments for context and future maintainers.
from __future__ import annotations

from typing import List, cast

try:
    from enum import StrEnum  # Python 3.11+
except ImportError:
    from backports.strenum import StrEnum  # Python 3.10

from .scaling import StatScaler, StatScaling


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

    def scaler(self, scaling: "StatScaling", mod: float = 0) -> "StatScaler":
        """
        Returns a StatScaler object for this ability score, with the given scaling type and modifier.
        Used for advanced stat scaling logic.
        """
        return StatScaler(self, scaling, mod)

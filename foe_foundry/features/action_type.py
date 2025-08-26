from enum import auto

try:
    from enum import StrEnum  # Python 3.11+
except ImportError:
    from backports.strenum import StrEnum  # Python 3.10


class ActionType(StrEnum):
    Feature = auto()
    Action = auto()
    BonusAction = auto()
    Reaction = auto()
    Legendary = auto()

    @property
    def caption(self) -> str:
        """Return a human-readable caption for the action type."""
        if self == ActionType.Feature:
            return "Feature"
        elif self == ActionType.Action:
            return "Action"
        elif self == ActionType.BonusAction:
            return "Bonus Action"
        elif self == ActionType.Reaction:
            return "Reaction"
        elif self == ActionType.Legendary:
            return "Legendary Action"
        else:
            raise ValueError(f"Unknown action type: {self}")

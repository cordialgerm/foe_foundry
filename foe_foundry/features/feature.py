from dataclasses import dataclass

from .action_type import ActionType


@dataclass
class Feature:
    name: str
    description: str
    action: ActionType
    recharge: int | None = None
    uses: int | None = None

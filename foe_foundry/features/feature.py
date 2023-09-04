from dataclasses import dataclass, field

from .action_type import ActionType


@dataclass
class Feature:
    name: str
    description: str
    action: ActionType
    recharge: int | None = None
    uses: int | None = None
    replaces_multiattack: int = 0
    hidden: bool = False
    title: str = field(init=False)

    def __post_init__(self):
        if self.recharge is not None:
            if self.recharge == 6:
                self.title = f"{self.name} (Recharge {self.recharge})"
            else:
                self.title = f"{self.name} (Recharge {self.recharge}-6)"
        elif self.uses is not None:
            self.title = f"{self.name} ({self.uses}/day)"
        else:
            self.title = self.name

    def __hash__(self) -> int:
        return self.name.__hash__()

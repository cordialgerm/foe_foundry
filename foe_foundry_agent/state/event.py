from dataclasses import dataclass

from .state import MonsterAgentState


@dataclass
class StateChangedEvent:
    state: MonsterAgentState
    node: str

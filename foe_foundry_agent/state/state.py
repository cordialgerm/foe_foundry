from __future__ import annotations

from typing import TypedDict

from ..human_input import HumanInputState
from ..intake import IntakeState
from ..messages import InMemoryHistory
from ..plan import PlanState
from ..review import ReviewState


class MonsterAgentState(TypedDict):
    history: InMemoryHistory

    intake: IntakeState | None
    human_input: HumanInputState | None
    plan: PlanState | None
    review: ReviewState | None

    stop: bool

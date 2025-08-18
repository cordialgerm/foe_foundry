from __future__ import annotations

from typing import TypedDict

from ..intake import IntakeState
from ..messages import InMemoryHistory
from ..plan import PlanState


class MonsterAgentState(TypedDict):
    history: InMemoryHistory

    intake: IntakeState | None
    plan: PlanState | None

    human_input_requested: str | None
    human_response_provided: str | None

    stop: bool

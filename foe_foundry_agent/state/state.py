from __future__ import annotations

from typing import TypedDict

from ..human_input import HumanInputState
from ..human_review import HumanReviewState
from ..intake import IntakeState
from ..messages import InMemoryHistory
from ..plan import PlanState


class MonsterAgentState(TypedDict):
    history: InMemoryHistory

    intake: IntakeState | None
    human_input: HumanInputState | None
    plan: PlanState | None
    human_review: HumanReviewState | None

    stop: bool

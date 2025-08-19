from .chain import initialize_intake_chain  # noqa
from .state import IntakeState
from ..messages import InMemoryHistory
from ..human_input import HumanInputState
from langchain_core.messages import AIMessage


async def run_intake_chain(
    history: InMemoryHistory,
) -> tuple[IntakeState | None, HumanInputState | None]:
    """Runs the intake chain for the given input and returns the IntakeState"""

    plan_chain = initialize_intake_chain()
    result: AIMessage = await plan_chain.ainvoke({"messages": history.messages})
    content: str = result.content  # type: ignore

    state = None
    follow_up = None

    try:
        state = IntakeState.from_llm_output(content)

        if not state.is_relevant:
            follow_up = "I'm here to talk about monsters. Please provide more information and try again."
        elif state.clarification_follow_up is not None:
            follow_up = state.clarification_follow_up
        else:
            history.add_ai_message("Intake complete.")

    except Exception:
        follow_up = "There was an issue with intake. Please provide more information and try again."

    if follow_up is not None:
        human_input = HumanInputState(input_requested=follow_up, return_node="intake")
    else:
        human_input = None

    return state, human_input

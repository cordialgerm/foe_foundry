from .chain import initialize_intake_chain  # noqa
from .state import IntakeState
from ..messages import InMemoryHistory
from langchain_core.messages import AIMessage


async def run_intake_chain(history: InMemoryHistory) -> IntakeState:
    """Runs the intake chain for the given input and returns the IntakeState"""

    plan_chain = initialize_intake_chain()
    result: AIMessage = await plan_chain.ainvoke({"messages": history.messages})
    content: str = result.content  # type: ignore
    state = IntakeState.from_llm_output(content)
    return state

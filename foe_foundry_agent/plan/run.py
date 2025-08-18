from .chain import initialize_plan_chain  # noqa
from .state import PlanState
from ..messages import InMemoryHistory
from langchain_core.messages import AIMessage


async def run_plan_chain(
    monster_input: str, history: InMemoryHistory
) -> PlanState | None:
    """Runs the plan chain for the given monster input and returns the PlanState"""

    plan_chain = initialize_plan_chain()
    result: AIMessage = await plan_chain.ainvoke(
        {"monster_input": monster_input, "messages": history.messages}
    )
    content: str = result.content  # type: ignore
    state = PlanState.from_llm_output(content)
    return state

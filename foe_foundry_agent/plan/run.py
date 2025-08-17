from .chain import initialize_plan_chain  # noqa
from .state import PlanState
from langchain_core.messages import AIMessage


async def run_plan_chain(monster_input: str) -> PlanState | None:
    """Runs the plan chain for the given monster input and returns the PlanState"""

    plan_chain = initialize_plan_chain()
    result: AIMessage = await plan_chain.ainvoke({"monster_input": monster_input})
    content: str = result.content  # type: ignore
    state = PlanState.from_llm_output(content)
    return state

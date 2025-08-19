from langchain_core.messages import AIMessage

from ..messages import InMemoryHistory
from ..plan import PlanState
from .chain import initialize_review_chain
from .state import ReviewState


async def run_review_chain(plan: PlanState, history: InMemoryHistory) -> ReviewState:
    """Runs the review chain for the given plan and returns the ReviewState"""

    review_chain = initialize_review_chain()
    result: AIMessage = await review_chain.ainvoke(
        {"plan": plan, "messages": history.messages}
    )
    content: str = result.content  # type: ignore
    state = ReviewState.from_llm_output(content)
    return state

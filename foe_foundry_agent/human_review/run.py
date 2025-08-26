from langchain_core.messages import AIMessage

from ..messages import InMemoryHistory
from .chain import initialize_review_chain
from .state import HumanReviewState


async def run_review_chain(
    review: HumanReviewState, history: InMemoryHistory
) -> HumanReviewState:
    """Runs the review chain for the given plan and returns the ReviewState"""

    review_chain = initialize_review_chain()
    result: AIMessage = await review_chain.ainvoke(
        {"review_request": review.review_requested, "messages": history.messages}
    )
    content: str = result.content  # type: ignore
    return review.with_llm_response(content)

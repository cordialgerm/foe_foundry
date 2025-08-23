from .chain import initialize_plan_chain  # noqa
from .state import PlanState
from ..messages import InMemoryHistory
from ..human_input import HumanInputState
from ..human_review import HumanReviewState
from langchain_core.messages import AIMessage


async def run_plan_chain(
    monster_input: str, history: InMemoryHistory
) -> tuple[PlanState | None, HumanInputState | None, HumanReviewState | None]:
    """Runs the plan chain for the given monster input and returns the PlanState"""

    plan_chain = initialize_plan_chain()
    result: AIMessage = await plan_chain.ainvoke(
        {"monster_input": monster_input, "messages": history.messages}
    )
    content: str = result.content  # type: ignore

    plan = None
    follow_up = None

    try:
        plan = PlanState.from_llm_output(content)

        if plan.missing_information_query:
            follow_up = plan.missing_information_query
        else:
            history.add_ai_message("Plan generation complete.")

    except Exception:
        follow_up = "There was an issue with plan generation. Please provide more information and try again."

    human_input = None
    human_review = None
    if follow_up is not None:
        history.add_ai_message(follow_up)
        human_input = HumanInputState(input_requested=follow_up, return_node="plan")
    else:
        human_review = HumanReviewState(
            review_requested="Do you have any changes you'd like to see to this plan, or do you approve it?",
            return_node="plan",
            next_node="research",
        )
        history.add_ai_message(human_review.review_requested)

    return plan, human_input, human_review

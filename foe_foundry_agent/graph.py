from typing import Literal

from langgraph.graph import StateGraph
from langgraph.types import Checkpointer, interrupt

from .intake import run_intake_chain
from .plan import run_plan_chain
from .state import MonsterAgentState


async def node_intake(state: MonsterAgentState) -> MonsterAgentState:
    history = state["history"]
    intake = await run_intake_chain(history)

    if intake is None:
        human_input_requested = "There was an issue with intake. Please provide more information and try again."
    elif intake.clarification_follow_up is not None:
        human_input_requested = intake.clarification_follow_up
    elif not intake.is_relevant:
        human_input_requested = "I'm here to talk about monsters. Please provide more information and try again."
    else:
        human_input_requested = None

    if human_input_requested is not None:
        history.add_ai_message(human_input_requested)

    return {**state, "human_input_requested": human_input_requested, "intake": intake}


def edges_intake(state: MonsterAgentState) -> Literal["human_input", "plan"]:
    if state["human_input_requested"] is not None:
        return "human_input"
    else:
        return "plan"


async def node_plan(state: MonsterAgentState) -> MonsterAgentState:
    history = state["history"]
    intake = state["intake"]
    if intake is None:
        raise ValueError("Intake state is required for plan generation.")

    monster_input = f"{intake.request_summary}\n\n\n{intake.statblock_details}"

    plan = await run_plan_chain(monster_input, state["history"])

    if plan is None:
        human_input_requested = "There was an issue with plan generation. Please provide more information and try again."
    elif plan.missing_information_query:
        human_input_requested = plan.missing_information_query
    else:
        human_input_requested = None

    if human_input_requested is not None:
        history.add_ai_message(human_input_requested)

    return {**state, "human_input_requested": human_input_requested, "plan": plan}


def edges_plan(state: MonsterAgentState) -> Literal["human_input", "__end__"]:
    if state.get("human_input_requested"):
        return "human_input"
    else:
        return "__end__"


# def node_plan_review(state: MonsterAgentState) -> MonsterAgentState:
#     # Get human feedback on the generated plan
#     # Or respond to human feedback on the generated plan
#     if state["human_response_provided"] is None:
#         return {
#             **state,
#             "human_input_requested": "Please review the plan and provide feedback or confirm if it is acceptable.",
#         }
#     else:
#         pass


async def node_human_input(state: MonsterAgentState) -> MonsterAgentState:
    result = interrupt({"human_input": "<HUMAN INPUT NEEDED>"})
    human_input = result.get("human_input", "")
    state["history"].add_user_message(human_input)
    return {
        **state,
        "human_input_requested": None,
        "human_response_provided": human_input,
    }


def entry_point(
    state: MonsterAgentState,
) -> Literal["intake", "plan", "human_input", "__end__"]:
    if state["human_input_requested"] is not None:
        return "human_input"
    elif state["intake"] is None:
        return "intake"
    elif state["intake"] is not None and state["plan"] is None:
        return "plan"
    else:
        return "__end__"


def build_planning_graph(checkpointer: Checkpointer):
    """Builds the langgraph planning graph"""

    builder = StateGraph(MonsterAgentState)
    builder.add_node("intake", node_intake)
    builder.add_node("plan", node_plan)
    builder.add_node("human_input", node_human_input)
    # builder.add_node("node_plan_review", node_plan_review)

    builder.set_conditional_entry_point(entry_point)
    builder.add_conditional_edges("intake", edges_intake)
    builder.add_conditional_edges("plan", edges_plan)
    # builder.add_conditional_edges("plan_review", edges_plan_review)

    plan_subgraph = builder.compile(checkpointer=checkpointer)
    return plan_subgraph

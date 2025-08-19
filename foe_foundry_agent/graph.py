from typing import Literal

from langgraph.graph import StateGraph
from langgraph.types import Checkpointer, interrupt

from .human_input import HumanInputState
from .intake import run_intake_chain
from .plan import run_plan_chain
from .state import MonsterAgentState


async def node_intake(state: MonsterAgentState) -> MonsterAgentState:
    history = state["history"]
    intake, human_input = await run_intake_chain(history)
    return {**state, "human_input": human_input, "intake": intake}


def edges_intake(state: MonsterAgentState) -> Literal["human_input", "plan"]:
    if state["human_input"] is not None:
        return "human_input"
    else:
        return "plan"


async def node_plan(state: MonsterAgentState) -> MonsterAgentState:
    history = state["history"]
    intake = state["intake"]
    if intake is None:
        raise ValueError("Intake state is required for plan generation.")

    monster_input = f"{intake.request_summary}\n\n\n{intake.statblock_details}"

    plan, human_input = await run_plan_chain(monster_input, history)
    return {
        **state,
        "human_input": human_input,
        "plan": plan,
        "stop": human_input is None,
    }


def edges_plan(state: MonsterAgentState) -> Literal["human_input", "__end__"]:
    if state.get("human_input"):
        return "human_input"
    else:
        return "__end__"


# async def node_review(state: MonsterAgentState) -> MonsterAgentState:
#     plan = state["plan"]
#     history = state["history"]
#     if plan is None:
#         raise ValueError("Plan state is required for review.")

#     history.add_ai_message("Do you approve this plan? If not, please provide feedback.")
#     result = interrupt({"human_input": state})
#     human_input = result.get("human_input", "Not Approved")

#     history.add_user_message(human_input)
#     review = await run_review_chain(plan, history)

#     if review.is_approved:
#         history.add_ai_message("Plan approved.")
#     else:
#         history.add_ai_message("Plan not approved.")
#     history.add_ai_message(review.to_llm_display_text())

#     return {**state, "review": review, "stop": review.is_approved}


# def edges_review(state: MonsterAgentState) -> Literal["plan", "__end__"]:
#     review = state.get("review")

#     if review and review.is_approved:
#         return "__end__"
#     else:
#         return "plan"


async def node_human_input(state: MonsterAgentState) -> MonsterAgentState:
    previously_requested = state["human_input"]
    if previously_requested is None:
        raise ValueError("Human input state is required for this node.")

    if previously_requested.input_provided is not None:
        human_input = previously_requested
    else:
        result = interrupt({"human_input": state["human_input"]})
        response = result.get("human_input", "")
        human_input = HumanInputState(
            input_requested=previously_requested.input_requested,
            return_node=previously_requested.return_node,
            input_provided=response,
        )

    state["history"].add_user_message(human_input.input_provided)  # type: ignore
    return {
        **state,
        "human_input": human_input,
    }


def edge_human_input(state: MonsterAgentState) -> Literal["intake", "plan", "__end__"]:
    if state["human_input"] is None:
        raise ValueError("Human input state is required for this edge.")

    return state["human_input"].return_node  # type: ignore


def entry_point(
    state: MonsterAgentState,
) -> Literal["intake", "plan", "human_input", "__end__"]:
    if state["human_input"] is not None:
        return state["human_input"].next_edge  # type: ignore
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

    builder.set_conditional_entry_point(entry_point)
    builder.add_conditional_edges("intake", edges_intake)
    builder.add_conditional_edges("plan", edges_plan)
    builder.add_conditional_edges("human_input", edge_human_input)

    plan_subgraph = builder.compile(checkpointer=checkpointer)
    return plan_subgraph

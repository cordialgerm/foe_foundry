from typing import Literal

from langgraph.graph import StateGraph
from langgraph.types import Checkpointer, interrupt

from .human_input import HumanInputState
from .human_review import run_review_chain
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

    plan, human_input, human_review = await run_plan_chain(monster_input, history)
    return {
        **state,
        "human_input": human_input,
        "plan": plan,
        "human_review": human_review,
    }


def edges_plan(
    state: MonsterAgentState,
) -> Literal["human_input", "human_review", "__end__"]:
    if state.get("human_input"):
        return "human_input"
    elif state.get("human_review"):
        return "human_review"
    else:
        return "__end__"


async def node_human_input(state: MonsterAgentState) -> MonsterAgentState:
    previously_requested = state["human_input"]
    if previously_requested is None:
        raise ValueError("Human input state is required for this node.")

    if previously_requested.input_provided is None:
        interrupt({"human_input": state["human_input"]})
        raise RuntimeError("Unreachable")  # unreachable from here
    else:
        human_input = previously_requested

    state["history"].add_user_message(human_input.input_provided)  # type: ignore
    return {
        **state,
        "human_input": human_input,
    }


def edge_human_input(state: MonsterAgentState) -> Literal["intake", "plan", "__end__"]:
    if state["human_input"] is None:
        raise ValueError("Human input state is required for this edge.")

    return state["human_input"].return_node  # type: ignore


async def node_human_review(state: MonsterAgentState) -> MonsterAgentState:
    history = state["history"]
    human_input = state["human_input"]
    previously_reviewed = state["human_review"]
    if previously_reviewed is None:
        raise ValueError("Human review state is required for this node.")

    if human_input is None:
        interrupt(
            {
                "human_input": HumanInputState(
                    input_requested=previously_reviewed.review_requested,
                    return_node=previously_reviewed.return_node,
                )
            }
        )
        raise RuntimeError("Unreachable")  # unreachable from here

    review_text = human_input.input_provided or ""
    review = previously_reviewed.with_human_response(review_text)
    history.add_user_message(review_text)

    review = await run_review_chain(review, history)

    if review.is_approved:
        history.add_ai_message("Approved.")
    else:
        history.add_ai_message("Not Approved.")

    return {
        **state,
        "human_review": review,
        "human_input": None,
        "stop": review.is_approved or False,
    }


def edge_human_review(state: MonsterAgentState) -> Literal["plan", "__end__"]:
    if state["human_review"] is None:
        raise ValueError("Human review state is required for this edge.")

    return state["human_review"].next_edge  # type: ignore


def entry_point(
    state: MonsterAgentState,
) -> Literal["intake", "plan", "human_input", "__end__"]:
    if state["human_input"] is not None:
        return state["human_input"].next_edge  # type: ignore
    elif state["human_review"] is not None:
        return state["human_review"].next_edge  # type: ignore
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
    builder.add_node("human_review", node_human_review)

    builder.set_conditional_entry_point(entry_point)
    builder.add_conditional_edges("intake", edges_intake)
    builder.add_conditional_edges("plan", edges_plan)
    builder.add_conditional_edges("human_input", edge_human_input)
    builder.add_conditional_edges("human_review", edge_human_review)

    plan_subgraph = builder.compile(checkpointer=checkpointer)
    return plan_subgraph

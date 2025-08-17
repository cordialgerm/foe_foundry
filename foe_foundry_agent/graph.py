from langgraph.graph import StateGraph

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
    else:
        human_input_requested = None

    if human_input_requested is not None:
        history.add_ai_message(human_input_requested)

    return {**state, "human_input_requested": human_input_requested, "intake": intake}


def edges_intake(state: MonsterAgentState) -> str:
    if state["human_input_requested"] is not None:
        return "human_input"
    else:
        return "plan"


async def node_plan(state: MonsterAgentState) -> MonsterAgentState:
    history = state["history"]
    intake = state["intake"]
    if intake is None:
        raise ValueError("Intake state is required for plan generation.")

    monster_input = (
        f"{intake.statblock_markdown or ''}\n\n\n{intake.additional_notes or ''}"
    )

    plan = await run_plan_chain(monster_input)

    if plan is None:
        human_input_requested = "There was an issue with plan generation. Please provide more information and try again."
    elif plan.missing_information_query:
        human_input_requested = plan.missing_information_query
    else:
        human_input_requested = None

    if human_input_requested is not None:
        history.add_ai_message(human_input_requested)

    return {**state, "human_input_requested": human_input_requested, "plan": plan}


def edges_plan(state: MonsterAgentState) -> str:
    if state.get("human_input_requested"):
        return "human_input"
    else:
        return "plan_review"


def node_plan_review(state: MonsterAgentState) -> MonsterAgentState:
    return state


def node_human_input(state: MonsterAgentState) -> MonsterAgentState:
    return state


plan_subgraph_builder = StateGraph(MonsterAgentState)
plan_subgraph_builder.add_node("intake", node_intake)
plan_subgraph_builder.add_node("plan", node_plan)
plan_subgraph_builder.add_node("human_input", node_human_input)
plan_subgraph_builder.add_node("node_plan_review", node_plan_review)

plan_subgraph_builder.set_entry_point("intake")
plan_subgraph_builder.add_conditional_edges("intake", edges_intake)
plan_subgraph_builder.add_conditional_edges("plan", edges_plan)

plan_subgraph = plan_subgraph_builder.compile()

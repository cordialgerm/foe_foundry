from typing import Literal

from langchain_core.messages import AIMessage, ToolCall
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import StateGraph
from langgraph.types import Checkpointer

from ..messages import InMemoryHistory
from ..plan import PlanState
from ..tools import ToolManager
from .chain import initialize_research_chain, initialize_summary_chain
from .state import ResearchNote, ResearchResult, ResearchState, parse_research_notes


async def node_research(state: ResearchState) -> ResearchState:
    messages = state["messages"]
    tools = ToolManager(
        budget_search_monsters=state["budget_search_monsters"],
        budget_search_powers=state["budget_search_powers"],
        budget_get_monster_details=state["budget_monster_details"],
    )
    chain = initialize_research_chain(tools)

    if state["force_exit"]:
        messages.add_system_message(
            "IMPORTANT: You must now produce the final output. Return exactly 1-3 fenced ```md code blocks using the schemas previously described. No other text."
        )
    elif budget := tools.describe_budget():
        messages.add_system_message(budget)

    response: AIMessage = await chain.ainvoke({"messages": messages.messages})

    tool_calls: list[ToolCall] | None = None
    notes: list[ResearchNote] | None = None

    if (
        hasattr(response, "tool_calls")
        and response.tool_calls is not None
        and len(response.tool_calls)
    ):
        tool_calls = response.tool_calls
    else:
        messages.add_ai_message(response.content)  # type: ignore
        try:
            notes = parse_research_notes(response.content)  # type: ignore
        except ValueError as x:
            messages.add_ai_message(
                "Failed to parse research notes. Please adjust the response content and try again. Here is the stack trace:\n\n"
                + str(x)
            )

    return {
        **state,
        "tool_calls": tool_calls,
        "notes": notes,
    }


def edge_research(
    state: ResearchState,
) -> Literal["tool", "research", "summary", "__end__"]:
    if state["tool_calls"] is not None:
        return "tool"
    elif state["notes"] is not None:
        return "summary"
    else:
        return "research"


async def node_tool(state: ResearchState) -> ResearchState:
    messages = state["messages"]

    tool_calls = state["tool_calls"]
    if tool_calls is None or len(tool_calls) == 0:
        messages.add_system_message(
            "No tool calls were pending so nothing was executed."
        )
        return state

    tools = ToolManager(
        budget_search_monsters=state["budget_search_monsters"],
        budget_search_powers=state["budget_search_powers"],
        budget_get_monster_details=state["budget_monster_details"],
    )

    for tool_call in tool_calls:
        messages.add_tool_call(tool_call)
        tool_msg = tools.invoke(tool_call)
        if isinstance(tool_msg, str):
            messages.add_ai_message(tool_msg)
        else:
            messages.add_tool_message(tool_msg)

    force_exit = (
        tools.budget_search_monsters <= 0
        and tools.budget_search_powers <= 0
        and tools.budget_get_monster_details <= 0
    )

    return {
        **state,
        **tools.updated_state,  # type: ignore
        "force_exit": force_exit,
    }


async def node_summarize(state: ResearchState) -> ResearchState:
    messages = state["messages"]
    chain = initialize_summary_chain()

    response: AIMessage = await chain.ainvoke({"messages": messages.messages})
    summary: str = response.content  # type: ignore
    messages.add_ai_message(summary)
    return {**state, "overall_summary": summary}


def build_research_graph(checkpointer: Checkpointer):
    builder = StateGraph(ResearchState)

    builder.add_node("research", node_research)
    builder.add_node("tool", node_tool)
    builder.add_node("summary", node_summarize)
    builder.set_entry_point("research")
    builder.add_conditional_edges("research", edge_research)
    builder.add_edge("tool", "research")
    builder.add_edge("summary", "__end__")

    research_subgraph = builder.compile(checkpointer=checkpointer)
    return research_subgraph


async def run_research_graph(
    session_id: str, plan: PlanState | str, history: InMemoryHistory
) -> ResearchResult:
    saver = InMemorySaver()
    graph = build_research_graph(checkpointer=saver)

    if isinstance(plan, PlanState):
        plan = plan.to_llm_display_text()

    history.add_user_message(
        f"This is information about the monster that I want you to research:\n\n{plan}"
    )

    state: ResearchState = {
        "messages": history,
        "notes": None,
        "tool_calls": None,
        "force_exit": False,
        "overall_summary": None,
        "budget_search_monsters": 3,
        "budget_search_powers": 3,
        "budget_monster_details": 3,
    }

    config = {"configurable": {"thread_id": session_id}}

    state: ResearchState = await graph.ainvoke(state, config=config)  # type: ignore
    notes = state["notes"]
    overall_summary = state["overall_summary"]
    if notes is None or overall_summary is None:
        raise ValueError("Research notes and overall summary are required.")

    return ResearchResult(
        messages=history, notes=notes, overall_summary=overall_summary
    )

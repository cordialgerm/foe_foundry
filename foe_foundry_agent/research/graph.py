from typing import Literal

from langchain_core.messages import AIMessage, ToolCall
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import StateGraph
from langgraph.types import Checkpointer

from ..messages import InMemoryHistory
from ..plan import PlanState
from ..tools import get_monster_detail, grep_monster_markdown, search_monsters
from .chain import initialize_research_chain, initialize_summary_chain
from .state import ResearchNote, ResearchResult, ResearchState, parse_research_notes


async def node_research(state: ResearchState) -> ResearchState:
    messages = state["messages"]
    chain = initialize_research_chain()

    turns = state["detail_tool_count"] + state["search_tool_count"]
    if turns >= 8:
        messages.add_system_message(
            "You have exceeded the maximum number of turns. Proceed immediately to generating the research outputs."
        )
    if state["should_exit"]:
        messages.add_system_message(
            "IMPORTANT: You must now produce the final output. Return exactly 1-3 fenced ```md code blocks using the schemas previously described. No other text."
        )

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

    search_tool_count = state.get("search_tool_count", 0)
    detail_tool_count = state.get("detail_tool_count", 0)
    for tool_call in tool_calls:
        tool_name = tool_call["name"].lower()
        selected_tool = {
            "search_monsters": search_monsters,
            "grep_monster_markdown": grep_monster_markdown,
            "get_monster_detail": get_monster_detail,
        }[tool_name]
        tool_msg = selected_tool.invoke(tool_call)

        if tool_name == "get_monster_detail":
            detail_tool_count += 1
        else:
            search_tool_count += 1

        messages.add_tool_call(tool_call)
        messages.add_tool_message(tool_msg)

    should_exit = False
    if detail_tool_count >= 3:
        should_exit = True
        messages.add_system_message(
            "You've loaded the maximum number of monster details. You must immediately stop retrieving monster details and proceed to generating the research outputs."
        )
    elif detail_tool_count >= 2:
        should_exit = True
        messages.add_system_message(
            "You've loaded the maximum number of monster details. You must immediately stop retrieving monster details and proceed to generating the research outputs."
        )
    elif search_tool_count >= 4:
        should_exit = True
        messages.add_system_message(
            "You've reached the maximum number of tool searches. You must immediately stop searching and proceed to retrieving monster details."
        )
    elif search_tool_count >= 3:
        should_exit = True
        messages.add_system_message(
            "You've searched a couple of times now. If you've found what you're looking for, please conclude searching and proceed to retrieving monster details. If not, you can make one more search."
        )

    return {
        **state,
        "search_tool_count": search_tool_count,
        "detail_tool_count": detail_tool_count,
        "should_exit": should_exit,
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
        "detail_tool_count": 0,
        "search_tool_count": 0,
        "notes": None,
        "tool_calls": None,
        "should_exit": False,
        "overall_summary": None,
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

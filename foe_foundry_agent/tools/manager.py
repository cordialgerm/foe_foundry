from langchain_core.messages import ToolCall, ToolMessage
from langchain_core.tools import tool

from .grep import grep_monster_markdown as grep_monster_markdown_inner
from .search import get_monster_detail as get_monster_detail_inner
from .search import search_monsters as search_monsters_inner
from .search import search_powers as search_powers_inner


class ToolManager:
    def __init__(
        self,
        budget_search_monsters: int,
        budget_search_powers: int,
        budget_get_monster_details: int,
    ):
        self.budget_search_monsters = budget_search_monsters
        self.budget_search_powers = budget_search_powers
        self.budget_get_monster_details = budget_get_monster_details

    @property
    def search_monsters_tool(self):
        @tool
        def search_monsters(keywords) -> str:
            """Search for monsters."""

            if self.budget_search_monsters <= 0:
                return "You have exhausted your budget for searching monsters."

            result = search_monsters_inner(keywords)
            self.budget_search_monsters -= 1
            return result

        return search_monsters

    @property
    def search_powers_tool(self):
        @tool
        def search_powers(keywords):
            """Search for powers."""

            if self.budget_search_powers <= 0:
                return "You have exhausted your budget for searching powers."
            result = search_powers_inner(keywords)
            self.budget_search_powers -= 1
            return result

        return search_powers

    @property
    def grep_monster_markdown_tool(self):
        @tool
        def grep_monster_markdown(*args, **kwargs) -> str:
            """Search for monsters in markdown."""

            if self.budget_search_monsters <= 0:
                return "You have exhausted your budget for searching monsters."
            result = grep_monster_markdown_inner(*args, **kwargs)
            self.budget_search_monsters -= 1
            return result

        return grep_monster_markdown

    @property
    def get_monster_detail_tool(self):
        @tool
        def get_monster_detail(*args, **kwargs) -> str:
            """Get details about a specific monster."""

            if self.budget_get_monster_details <= 0:
                return "You have exhausted your budget for getting monster details."
            result = get_monster_detail_inner(*args, **kwargs)
            self.budget_get_monster_details -= 1
            return result

        return get_monster_detail

    def describe_budget(self) -> str | None:
        messages = []

        if self.budget_search_monsters <= 0:
            messages.append(
                "You have exhausted your budget for searching monsters. You must immediately stop searching for monsters and proceed to searching for powers and loading specific monster details."
            )
        if self.budget_search_monsters <= 1:
            messages.append(
                "You are running low on your budget for searching monsters. Consider focusing on searching for powers or loading specific monster details."
            )

        if self.budget_search_powers <= 0:
            messages.append(
                "You have exhausted your budget for searching powers. You must immediately stop searching for powers and proceed to the next step."
            )
        if self.budget_search_powers <= 1:
            messages.append(
                "You are running low on your budget for searching powers. Consider focusing on the next step."
            )

        if self.budget_get_monster_details <= 0:
            messages.append(
                "You have exhausted your budget for getting monster details. You must immediately stop retrieving monster details and proceed to generating the research outputs."
            )

        if self.budget_get_monster_details <= 1:
            messages.append(
                "You are running low on your budget for getting monster details. Consider focusing on generating the research outputs."
            )

        if len(messages):
            return "\n".join(messages)
        else:
            return None

    def invoke(self, tool_call: ToolCall) -> ToolMessage | str:
        tool_name = tool_call["name"].lower()
        selected_tool = {
            "search_monsters": self.search_monsters_tool,
            "search_powers": self.search_powers_tool,
            "grep_monster_markdown": self.grep_monster_markdown_tool,
            "get_monster_detail": self.get_monster_detail_tool,
        }.get(tool_name)

        if selected_tool is None:
            return f"Tool '{tool_name}' not recognized."

        try:
            return selected_tool.invoke(tool_call)
        except Exception as x:
            return f"An error occurred while executing tool '{tool_name}': {x}"

    @property
    def tools(self) -> list:
        # IMPORTANT - we return the underlying tool (not the wrapped tools)
        # This is because we want the LLM to see the rich docstrings of the original tools
        # When the ToolCall is issued, we use invoke() above to actually dispatch it
        # That will ensure the wrapped tool is what is actually executed
        return [
            search_monsters_inner,
            search_powers_inner,
            grep_monster_markdown_inner,
            get_monster_detail_inner,
        ]

    @property
    def updated_state(self) -> dict:
        return {
            "budget_search_monsters": self.budget_search_monsters,
            "budget_search_powers": self.budget_search_powers,
            "budget_monster_details": self.budget_get_monster_details,
        }

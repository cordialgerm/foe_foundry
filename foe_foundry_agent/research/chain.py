from pathlib import Path

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import Runnable
from langchain_openai import ChatOpenAI

from ..tools import grep_monster_markdown, search_monsters


def initialize_research_chain(
    model: str | None = None,
) -> Runnable:
    """Initialize the initial input chain, which handles initial ingestion for the monster agent. Expects {messages} variables."""

    if model is None:
        model = "gpt-5"

    llm = ChatOpenAI(temperature=0.3, model=model, streaming=False)

    tools = [search_monsters, grep_monster_markdown, grep_monster_markdown]
    llm_with_tools = llm.bind_tools(tools, tool_choice="auto")

    # Load the system prompt text
    prompt_path = Path(__file__).parent / "prompt.md"
    prompt_text = prompt_path.read_text(encoding="utf-8")

    # Build a chat prompt
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", prompt_text),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )

    return prompt | llm_with_tools

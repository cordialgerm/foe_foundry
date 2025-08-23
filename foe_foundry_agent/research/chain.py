import textwrap
from pathlib import Path

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import Runnable
from langchain_openai import ChatOpenAI

from ..tools import grep_monster_markdown, search_monsters


def initialize_research_chain(
    model: str | None = None,
) -> Runnable:
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


def initialize_summary_chain(
    model: str | None = None,
) -> Runnable:
    if model is None:
        model = "gpt-5"

    llm = ChatOpenAI(temperature=0.3, model=model, streaming=False)

    # Load the system prompt text
    prompt_text = textwrap.dedent('''Summarize this subgraph message history about a monster research plan into a high-level summary paragraph the discusses what was researched and describes the main findings. \
        This summary should be suitable to show in a parent agent's context so that the user can understand what happened during this long research sub-graph.\n\n \
        The message should begin with a suitable greeting similar to "Here is what we researched..."''')

    # Build a chat prompt
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", prompt_text),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )

    return prompt | llm

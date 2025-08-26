from pathlib import Path

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import Runnable
from langchain_openai import ChatOpenAI


def initialize_plan_chain(
    model: str | None = None,
) -> Runnable:
    """Initialize the plan chain, which handles overall planning for the monster agent. Expects {monster_input} and {messages} variables."""

    if model is None:
        model = "gpt-5-mini"

    llm = ChatOpenAI(temperature=0.3, model=model, streaming=False)
    # Load the system prompt text
    prompt_path = Path(__file__).parent / "prompt.md"
    prompt_text = prompt_path.read_text(encoding="utf-8")

    # Build a chat prompt
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", prompt_text),
            MessagesPlaceholder(variable_name="messages"),  # message history goes here
            ("human", "{monster_input}"),
        ]
    )

    return prompt | llm

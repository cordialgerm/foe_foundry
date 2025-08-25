from pathlib import Path

import dotenv
from langchain_core.messages import BaseMessage

from ..events import add_message_listener
from ..messages import InMemoryHistory
from .graph import run_research_graph


def _message_listener(message: BaseMessage, history):
    print(f"{message.type}:\n{message.content}")


async def run_console_research():
    add_message_listener(_message_listener)
    dotenv.load_dotenv()
    history = InMemoryHistory()
    greeting = "This is the start of the monster research agent\n"
    print(greeting)

    monster_plan = input("Enter your research query (or 'exit' to quit): ")
    if monster_plan.lower() == "exit":
        return

    await run_research_graph("console-session", monster_plan, history)
    print("DONE!")

    output_dir = Path.cwd() / "cache" / "foe_foundry_agent" / "research"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "monster_research_output.md"
    with open(output_file, "w") as f:
        f.write("# Monster Research Output\n")
        f.write("---\n")
        f.write(str(history))

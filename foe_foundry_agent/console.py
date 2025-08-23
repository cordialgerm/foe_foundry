import asyncio
import json
from pathlib import Path

import dotenv
from langchain_core.messages import BaseMessage

from .messages import InMemoryHistory, add_message_listener
from .run import GraphRunner


async def run_async():
    h = InMemoryHistory()
    add_message_listener(on_message_received)
    g = GraphRunner(input_callback=human_input)
    state = await g.run_async(session_id="test-console-session", history=h)

    dir = Path.cwd() / "cache" / "foe_foundry_agent"
    dir.mkdir(parents=True, exist_ok=True)

    log_file = dir / "console_run_output.md"
    with log_file.open("w") as f:
        f.write("# Console Run Output\n")
        f.write("---\n")
        f.write(str(h))

    state_file = dir / "console_run_state.json"
    keys = {}
    state["intake"]
    state["plan"]
    state["research"]

    with state_file.open("w") as f:
        keys = {"intake", "plan", "research"}
        json_data = {k: v.model_dump_json() for k, v in state.items() if k in keys}  # type: ignore
        json.dump(json_data, f)

    print("DONE!")


def on_message_received(message: BaseMessage, history):
    print(f"{message.type}:\n{message.content}")


def human_input() -> str:
    return input("You: ")


def run():
    dotenv.load_dotenv()
    asyncio.run(run_async())


if __name__ == "__main__":
    run()

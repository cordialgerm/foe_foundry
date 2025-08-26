import asyncio
import json
from pathlib import Path

import dotenv
from langchain_core.messages import BaseMessage

from .events import add_message_listener, add_state_listener
from .messages import InMemoryHistory
from .run import GraphRunner
from .state import StateChangedEvent


async def run_async():
    h = InMemoryHistory()
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

    with state_file.open("w") as f:
        keys = {"intake", "plan", "research"}
        json_data = {
            k: v.model_dump(mode="json") if v is not None else v  # type: ignore
            for k, v in state.items()
            if k in keys
        }
        json.dump(json_data, f)

    print("DONE!")


def on_state_changed(event: StateChangedEvent):
    state = event.state

    if state["research"] is not None:
        print(state["research"].to_llm_display_text())
    elif state["plan"] is not None:
        print(state["plan"].to_llm_display_text())
    elif state["intake"] is not None:
        print(state["intake"].to_llm_display_text())


def on_message_received(message: BaseMessage, history):
    print(f"{message.type}:\n{message.content}")


def human_input() -> str:
    try:
        return input("You: ")
    except KeyboardInterrupt:
        return "exit"


def run():
    dotenv.load_dotenv()
    add_message_listener(on_message_received)
    add_state_listener(on_state_changed)
    asyncio.run(run_async())


if __name__ == "__main__":
    run()

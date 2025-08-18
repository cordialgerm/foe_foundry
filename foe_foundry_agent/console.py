import asyncio

import dotenv
from langchain_core.messages import AIMessage
from langgraph.types import Command

from .graph import plan_subgraph
from .state import InMemoryHistory, MonsterAgentState


class RunInConsole:
    def __init__(self):
        self.printed_ids = set()

    def _print_message_history(self, state: MonsterAgentState):
        """Prints the message history from the state."""
        for message in state["history"].messages:
            if message.id in self.printed_ids:
                continue

            self.printed_ids.add(message.id)
            if isinstance(message, AIMessage):
                print("Codex: ", message.content)

    def _human_input(self) -> Command | None:
        user_input = input("\nYou: ").strip()
        if user_input.lower() in {"exit", "quit"}:
            return None
        else:
            return Command(resume={"human_input": user_input})

    async def run_async(self):
        greeting = "Welcome! I'm Cordialgerm's Codex, your AI Assistant for Foe Foundry. I can help you create new monster statblocks.\n\nPlease start by describing or pasting in the markdown of the monster you want to create.\n"

        history = InMemoryHistory()
        history.add_ai_message(greeting)

        session_id = "test_console_session"
        config = {"configurable": {"thread_id": session_id}}

        original_state: MonsterAgentState = {
            "history": history,
            "intake": None,
            "plan": None,
            "human_input_requested": greeting,
            "human_response_provided": None,
            "stop": False,
        }

        state = original_state
        while True:
            state, stop = await self._next_turn(state, config)
            if stop or state is None:
                print("Done!")
                break

    async def _next_turn(
        self, state: MonsterAgentState | Command, config: dict
    ) -> tuple[MonsterAgentState | Command | None, bool]:
        """Handles the next turn in the conversation."""

        result: dict = await plan_subgraph.ainvoke(input=state, config=config)  # type: ignore

        if "__interrupt__" in result:
            command = self._human_input()
            return command, command is None
        else:
            new_state: MonsterAgentState = await plan_subgraph.ainvoke(
                input=state,
                config=config,  # type: ignore
            )
            stop = new_state.get("stop", False)
            return new_state, stop


def run():
    dotenv.load_dotenv()
    r = RunInConsole()
    asyncio.run(r.run_async())


if __name__ == "__main__":
    run()

import asyncio
from typing import Any

import dotenv
from langchain_core.messages import AIMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

from .graph import build_planning_graph
from .human_input import HumanInputState
from .state import InMemoryHistory, MonsterAgentState


class RunInConsole:
    def __init__(self):
        self.printed_ids = set()
        self.saver = InMemorySaver()
        self.graph = build_planning_graph(self.saver)
        self.state_printed = set()

    def _print_message_history(self, state: MonsterAgentState | Any):
        """Prints the message history from the state."""

        if not isinstance(state, dict) or "history" not in state:
            return

        for message in state["history"].messages:
            if message.id in self.printed_ids:
                continue

            self.printed_ids.add(message.id)
            if isinstance(message, AIMessage):
                print("Codex: ", message.content)

    def _print_state(self, state: MonsterAgentState | Any):
        if not isinstance(state, dict):
            return

        intake = state.get("intake")
        if intake is not None and "intake" not in self.state_printed:
            self.state_printed.add("intake")
            print("Intake: ", intake.to_llm_display_text())

        plan = state.get("plan")
        if plan is not None and "plan" not in self.state_printed:
            self.state_printed.add("plan")
            print("Plan: ", plan.to_yaml_text())

        # review = state.get("review")
        # if review is not None and "review" not in self.state_printed:
        #     self.state_printed.add("review")
        #     print("Review: ", review.to_llm_display_text())

    def _human_input(self, human_input: HumanInputState) -> Command | None:
        user_input = input("\nYou: ").strip()
        if user_input.lower() in {"exit", "quit"}:
            return None
        else:
            new_human_input = human_input.with_response(user_input)
            return Command(
                update={"human_input": new_human_input},
                goto=new_human_input.return_node,
            )

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
            "human_input": HumanInputState(
                input_requested=greeting, return_node="intake"
            ),
            "review": None,
            "stop": False,
        }

        self._print_message_history(original_state)
        self._print_state(original_state)
        state = original_state

        while True:
            needs_input = False
            async for update in self.graph.astream(
                input=state,  # type: ignore
                config=config,  # type: ignore
                stream_mode="updates",
            ):
                if "__interrupt__" in update:
                    state: MonsterAgentState = update["__interrupt__"][0].value  # type: ignore
                    self._print_state(state)
                    self._print_message_history(state)
                    needs_input = True
                    break
                else:
                    node = list(update.keys())[0]
                    state: MonsterAgentState = update[node]
                    self._print_state(state)
                    self._print_message_history(state)

            if needs_input:
                state = self._human_input(state["human_input"])  # type: ignore
                needs_input = False
                if state is None:
                    print("exiting...")

            if isinstance(state, dict) and state.get("stop", False):
                break

        print("\n----CHATBOT COMPLETED-----")


def run():
    dotenv.load_dotenv()
    r = RunInConsole()
    asyncio.run(r.run_async())


if __name__ == "__main__":
    run()

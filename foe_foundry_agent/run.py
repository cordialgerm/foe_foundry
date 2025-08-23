from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

from .graph import build_planning_graph
from .human_input import HumanInputState
from .state import InMemoryHistory, MonsterAgentState


class GraphRunner:
    def __init__(self, input_callback):
        self.printed_ids = set()
        self.saver = InMemorySaver()
        self.graph = build_planning_graph(self.saver)
        self.last_intake = None
        self.last_plan = None
        self.input_callback = input_callback

    def human_input(self, human_input: HumanInputState) -> Command | None:
        user_input = self.input_callback()
        if user_input is None or user_input.lower() in {"exit", "quit"}:
            return None
        else:
            new_human_input = human_input.with_response(user_input)
            return Command(
                update={"human_input": new_human_input},
            )

    async def run_async(
        self, session_id: str, history: InMemoryHistory
    ) -> MonsterAgentState:
        greeting = "Welcome! I'm Cordialgerm's Codex, your AI Assistant for Foe Foundry. I can help you create new monster statblocks.\n\nPlease start by describing or pasting in the markdown of the monster you want to create.\n"
        history.add_ai_message(greeting)

        config = {"configurable": {"thread_id": session_id}}

        original_state: MonsterAgentState = {
            "session_id": session_id,
            "history": history,
            "intake": None,
            "plan": None,
            "human_input": HumanInputState(
                input_requested=greeting, return_node="intake"
            ),
            "human_review": None,
            "research": None,
            "stop": False,
        }

        state: MonsterAgentState | Command = original_state

        while True:
            needs_input = False
            async for update in self.graph.astream(
                input=state,  # type: ignore
                config=config,  # type: ignore
                stream_mode="updates",
            ):
                if "__interrupt__" in update:
                    state = update["__interrupt__"][0].value  # type: ignore
                    needs_input = True
                    break
                else:
                    node = list(update.keys())[0]
                    state = update[node]

            if needs_input:
                state = self.human_input(state["human_input"])  # type: ignore
                needs_input = False

            if isinstance(state, dict) and state.get("stop", False):
                break

        return state

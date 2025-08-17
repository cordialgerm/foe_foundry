import asyncio

import dotenv

from .graph import plan_subgraph
from .state import InMemoryHistory, MonsterAgentState


async def run_async():
    dotenv.load_dotenv()

    greeting = "Welcome! I'm Cordialgerm's Codex, your AI Assistant for Foe Foundry. I can help you create new monster statblocks.\n\nPlease start by describing or pasting in the markdown of the monster you want to create."

    print(greeting)

    history = InMemoryHistory()
    history.add_ai_message(greeting)

    state: MonsterAgentState = {
        "history": history,
        "intake": None,
        "plan": None,
        "human_input_requested": None,
        "human_response_provided": None,
    }

    initial_input = input("Enter the monster information...")
    history.add_user_message(initial_input)

    result_state: MonsterAgentState = await plan_subgraph.ainvoke(state)  # type: ignore

    intake = result_state["intake"]
    if intake is not None:
        print(intake.to_llm_display_text())

    plan = result_state["plan"]
    if plan is not None:
        print(plan.to_yaml_text(fence=True))


def run():
    asyncio.run(run_async())


if __name__ == "__main__":
    run()

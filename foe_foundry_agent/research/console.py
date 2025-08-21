from pathlib import Path

import dotenv
from langchain_core.messages import AIMessage

from ..messages import InMemoryHistory
from ..tools import grep_monster_markdown, search_monsters
from .chain import initialize_research_chain


def start_console_research():
    history = InMemoryHistory()
    chain = initialize_research_chain()
    greeting = "This is the start of the monster research agent\n"
    print(greeting)

    monster_plan = input("Enter your research query (or 'exit' to quit): ")
    if monster_plan.lower() == "exit":
        return

    history.add_user_message(
        f"Here is a summary of the monster concept that I want you to research:\n\n{monster_plan}"
    )
    history.add_user_message(
        "So far, nothing has been researched by you yet. You will start the research!"
    )

    tool_count = 0

    while True:
        response: AIMessage = chain.invoke(
            {
                "messages": history.messages,
            }
        )

        if hasattr(response, "tool_calls") and response.tool_calls and tool_count < 5:
            for tool_call in response.tool_calls:
                selected_tool = {
                    "search_monsters": search_monsters,
                    "grep_monster_markdown": grep_monster_markdown,
                }[tool_call["name"].lower()]
                tool_msg = selected_tool.invoke(tool_call)
                content = tool_msg.content

                history.add_tool_call(tool_call)
                history.add_tool_message(tool_msg)

                print(f"Tool: {tool_call}\n")
                print(tool_msg.content)

                tool_count += 1

            if tool_count >= 5:
                history.add_user_message(
                    "You've reached the maximum number of tool searches. Please conclude your research immediately. Future tool calls will be ignored."
                )
            elif tool_count >= 3:
                history.add_user_message(
                    "You've searched a couple of times now. If you've found what you're looking for, please conclude and generate the research outputs. Otherwise, you can make one more search"
                )

        else:
            content: str = response.content  # type: ignore
            history.add_ai_message(content)
            print("AI: ", content)

        print("\n\n------- HISTORY ------\n\n")
        print(str(history))

        if "```md" in content:
            print("DONE!")
            break

        print("Press Enter to Continue...")
        input()
        print("Analyzing...")

    output_dir = Path.cwd() / "cache" / "foe_foundry_agent"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "monster_research_output.md"
    with open(output_file, "w") as f:
        f.write("# Monster Research Output\n")
        f.write("---\n")
        f.write(str(history))


if __name__ == "__main__":
    dotenv.load_dotenv()
    start_console_research()

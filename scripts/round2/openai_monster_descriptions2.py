import json
import os
from pathlib import Path

from openai import OpenAI


def main():
    client = OpenAI(api_key=os.environ.get("oai"))

    monster_dir = Path(__file__).parent.parent / "data" / "5e_canonical"
    summarization_dir = Path(__file__).parent.parent / "data" / "5e_nl2"
    summarization_dir.mkdir(exist_ok=True, parents=True)

    monsters = monster_dir.rglob("*.md")

    for monster_path in monsters:
        monster_md = monster_path.read_text(encoding="utf-8")
        summarization_path = summarization_dir / (monster_path.stem + ".json")
        if summarization_path.exists():
            continue

        print(f"Summarizing {monster_path}...")
        summary = summarize_monster(client, monster_md)

        if summary is not None:
            with summarization_path.open("w", encoding="utf-8") as f:
                json.dump(summary, f, indent=4)


def summarize_monster(client: OpenAI, markdown: str) -> dict | None:
    prompt_path = Path(__file__).parent / "system_prompt2.txt"
    prompt = prompt_path.read_text()

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": prompt,
            },
            {
                "role": "user",
                "content": "The markdown creature is below:\n" + markdown,
            },
        ],
    )

    content_text = completion.choices[0].message.content
    if content_text is None:
        print("EMPTY RESPONSE!")
        return None

    try:
        return json.loads(content_text)
    except ValueError as x:
        print(f"UNABLE TO PARSE JSON: {x}")
        return None


if __name__ == "__main__":
    print("TEST")
    main()

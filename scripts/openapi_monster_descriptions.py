import os
from pathlib import Path

from openai import OpenAI


def main():
    client = OpenAI(api_key=os.environ.get("oai"))

    monster_dir = Path(__file__).parent.parent.parent / "data" / "5e_artisinal_monsters"
    translation_dir = Path(__file__).parent.parent.parent / "data" / "5e_nl"

    monsters = monster_dir.rglob("*.md")

    for monster_path in monsters:
        monster_md = monster_path.read_text(encoding="utf-8")
        translation_path = translation_dir / monster_path.name
        if translation_path.exists():
            continue

        print(f"Translating {monster_path}...")
        translation = translate_monster(client, monster_md)

        if translation is not None:
            translation_path.write_text(translation, encoding="utf-8")


def translate_monster(client: OpenAI, markdown: str) -> str | None:
    prompt_path = Path(__file__).parent / "system_prompt.txt"
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
                "content": "The markdown monster to translate is below:\n" + markdown,
            },
        ],
    )

    return completion.choices[0].message.content


if __name__ == "__main__":
    main()

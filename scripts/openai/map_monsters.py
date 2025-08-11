import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List

import dotenv
from openai import OpenAI
from tqdm import tqdm

from foe_foundry.utils import name_to_key

dotenv.load_dotenv(Path.cwd() / ".env")
CLIENT = OpenAI()
MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
IN_DIR = Path.cwd() / "data" / "5e_nl2"
OUT_DIR = Path.cwd() / "data" / "5e_to_srd"
OUT_DIR.mkdir(parents=True, exist_ok=True)
PROMPT = Path(__file__).parent / "map_monsters_prompt.md"


def build_prompt(monster: dict) -> list[dict]:
    system = PROMPT.read_text().strip()
    return [
        {"role": "system", "content": system},
        {
            "role": "user",
            "content": f"This is the monster to map to a homebrew monster: ```json\n{json.dumps(monster)}\n```",
        },
    ]


def extract_json_block_from_text(text: str) -> Any:
    """
    Extracts a JSON block from a given text string.
    """
    matches = re.findall(r"```json(.*?)```", text, re.DOTALL)
    if matches:
        return json.loads(matches[0].strip())

    return json.loads(text.strip())


def call_llm(messages: List[Dict[str, str]], retries=2) -> dict:
    resp = CLIENT.responses.create(
        model=MODEL,
        input=messages,  # type: ignore
        temperature=0,
        top_p=1,
        max_output_tokens=450,
    )

    text = resp.output_text
    data = extract_json_block_from_text(text)
    return data


def process_one(monster_data: dict):
    monster_key = name_to_key(monster_data["name"])
    messages = build_prompt(monster_data)
    data = call_llm(messages)
    data["monster_key"] = monster_key

    # Save both final mapping and notes for audit
    out_dir = OUT_DIR / f"{monster_key}.json"
    out_dir.write_text(json.dumps(data, indent=2))


def main():
    files = sorted([f for f in IN_DIR.glob("*.json") if f.is_file()])
    processed_count = 0

    tqdm.write(f"Using model: {MODEL}")
    tqdm.write(f"Found {len(files)} files to process")

    progress_bar = tqdm(files, desc="Processing monsters")

    for fp in progress_bar:
        monster_data = json.loads(fp.read_text())
        name = monster_data["name"]
        monster_key = name_to_key(name)

        output_path = OUT_DIR / f"{monster_key}.json"
        if output_path.exists():
            continue

        try:
            process_one(monster_data)
            processed_count += 1

            progress_bar.set_postfix(
                {
                    "processed": processed_count,
                }
            )

        except Exception as e:
            tqdm.write(f"[ERROR] {fp}: {e}")


if __name__ == "__main__":
    main()

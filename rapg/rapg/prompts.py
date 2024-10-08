from pathlib import Path
from dataclasses import dataclass
import json


@dataclass
class Prompt:
    prompt: str
    answer: str


def load_prompts() -> list[Prompt]:
    with (Path(__file__).parent.parent / "prompts" / "prompts.json").open("r") as f:
        data = json.load(f)
        return [Prompt(**d) for d in data]

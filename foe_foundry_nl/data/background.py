import json
import math
import re
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from datasets import Dataset, DatasetDict

from .monsters.load import get_5e_srd_monster_descriptions


@dataclass
class BackgroundInfo:
    path: Path
    topic: str
    name: str
    text: str

    @property
    def word_count(self) -> int:
        return len(re.findall(r"\w+", self.text))

    def to_dict(self) -> dict[str, str]:
        return {
            "topic": self.topic,
            "name": self.name,
            "text": self.text,
        }


def iter_background_info() -> Iterable[BackgroundInfo]:
    yield from iter_5e_srd_spells()
    yield from iter_5e_srd_creature_types()
    yield from iter_5e_srd_misc_markdown_files()
    yield from iter_lgmrd_misc_markdown_files()
    yield from iter_mkwtd_markdown_files()


def iter_5e_srd_spells() -> Iterable[BackgroundInfo]:
    dir = Path(__file__).parent.parent.parent / "data" / "5esrd" / "Spells"

    for spell_file in dir.glob("*.md"):
        with spell_file.open("r", encoding="utf-8") as f:
            spell = spell_file.name[:-3]
            text = f.read()
            yield BackgroundInfo(path=spell_file, topic="spell", name=spell, text=text)


def iter_5e_srd_creature_types() -> Iterable[BackgroundInfo]:
    path = (
        Path(__file__).parent.parent.parent / "data" / "custom" / "creature_types.json"
    )

    with path.open("r", encoding="utf-8") as f:
        creature_types = json.load(f)
        for item in creature_types:
            creature_type = item["creature_type"]
            description = item["description"]
            examples = item["examples"]
            yield BackgroundInfo(
                path=path,
                topic="creature_type",
                name=creature_type,
                text=description + f"\n\nExamples: {examples}",
            )


def iter_5e_srd_misc_markdown_files() -> Iterable[BackgroundInfo]:
    base_path = Path(__file__).parent.parent.parent / "data" / "5esrd"
    exclude_dirs = ["Monsters", "Monsters (Alt)"]

    for file_path in base_path.rglob("*.md"):
        if not any(exclude_dir in file_path.parts for exclude_dir in exclude_dirs):
            with file_path.open("r", encoding="utf-8") as f:
                name = file_path.stem
                try:
                    text = f.read()
                    yield BackgroundInfo(
                        path=file_path, topic="5e_srd", name=name, text=text
                    )
                except Exception as x:
                    print(f"UNABLE TO PARSE {file_path}. {x}")


def iter_lgmrd_misc_markdown_files() -> Iterable[BackgroundInfo]:
    base_path = Path(__file__).parent.parent.parent / "data" / "lgmrd"
    dirs = [
        base_path / "markdown_obsidian_5e_monster_builder",
        base_path / "markdown_obsidian",
    ]

    for dir in dirs:
        for file_path in dir.rglob("*.md"):
            with file_path.open("r", encoding="utf-8") as f:
                try:
                    text = f.read()
                    yield BackgroundInfo(
                        path=file_path, topic="lgmrd", name=file_path.stem, text=text
                    )
                except Exception as x:
                    print(f"UNABLE TO PARSE {file_path}. {x}")


def iter_mkwtd_markdown_files() -> Iterable[BackgroundInfo]:
    dir = Path(__file__).parent.parent.parent / "data" / "the_monsters_know"
    for file_path in dir.rglob("*.md"):
        text = file_path.read_text(encoding="utf-8")
        name = text.split("\n")[0].replace("#", "").strip()
        yield BackgroundInfo(path=file_path, topic="mkwtd", name=name, text=text)


def load_background_dataset() -> tuple[DatasetDict, int, int]:
    docs = [b.to_dict() for b in iter_background_info()]

    rng = np.random.default_rng(20240711)
    indexes = np.arange(len(docs), dtype=int)
    rng.shuffle(indexes)
    n_test = math.floor(0.1 * len(docs))
    n_train = len(docs) - n_test

    train_dataset = Dataset.from_list([docs[i] for i in indexes[:n_train]])
    test_dataset = Dataset.from_list([docs[i] for i in indexes[n_train:]])

    descriptions = get_5e_srd_monster_descriptions()
    validation_dataset = Dataset.from_list(
        [dict(text="description") for _, description in descriptions.items()]
    )

    return (
        DatasetDict(
            {
                "train": train_dataset,
                "test": test_dataset,
                "validation": validation_dataset,
            }
        ),
        n_train,
        n_test,
    )


if __name__ == "__main__":
    infos = np.array([i.word_count for i in iter_background_info()])

    print(f"Loaded {len(infos)} background documents")
    print(f"Average Word Count of {np.mean(infos):.2f}")

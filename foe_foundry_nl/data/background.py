import json
from collections.abc import Iterable
from pathlib import Path

from .paragraph import TrainingParagraph
from .utils import split_by_paragraphs, split_markdown_by_headers


def iter_background_info() -> Iterable[TrainingParagraph]:
    yield from iter_5e_srd_spells()
    yield from iter_5e_srd_creature_types()
    yield from iter_5e_srd_misc_markdown_files()
    yield from iter_lgmrd_misc_markdown_files()
    yield from iter_mkwtd_markdown_files()


def iter_5e_srd_spells() -> Iterable[TrainingParagraph]:
    dir = Path(__file__).parent.parent.parent / "data" / "5esrd" / "Spells"

    for spell_file in dir.glob("*.md"):
        with spell_file.open("r", encoding="utf-8") as f:
            spell = spell_file.name[:-3]
            text = f.read()
            yield TrainingParagraph(topic="spell", name=spell, text=text)


def iter_5e_srd_creature_types() -> Iterable[TrainingParagraph]:
    path = (
        Path(__file__).parent.parent.parent / "data" / "custom" / "creature_types.json"
    )

    with path.open("r", encoding="utf-8") as f:
        creature_types = json.load(f)
        for item in creature_types:
            creature_type = item["creature_type"]
            description = item["description"]
            examples = item["examples"]
            yield TrainingParagraph(
                topic="creature_type",
                name=creature_type,
                text=description + f"\n\nExamples: {examples}",
            )


def iter_5e_srd_misc_markdown_files() -> Iterable[TrainingParagraph]:
    base_path = Path(__file__).parent.parent.parent / "data" / "5esrd"
    exclude_dirs = ["Monsters", "Monsters (Alt)"]

    for file_path in base_path.rglob("*.md"):
        if not any(exclude_dir in file_path.parts for exclude_dir in exclude_dirs):
            with file_path.open("r", encoding="utf-8") as f:
                name = file_path.stem
                try:
                    text = f.read()
                    for paragraph in split_markdown_by_headers(text):
                        yield TrainingParagraph(
                            topic="5e_srd", name=name, text=paragraph
                        )
                except Exception as x:
                    print(f"UNABLE TO PARSE {file_path}. {x}")


def iter_lgmrd_misc_markdown_files() -> Iterable[TrainingParagraph]:
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
                    for paragraph in split_markdown_by_headers(text):
                        yield TrainingParagraph(
                            topic="lgmrd", name=file_path.stem, text=paragraph
                        )
                except Exception as x:
                    print(f"UNABLE TO PARSE {file_path}. {x}")


def iter_mkwtd_markdown_files() -> Iterable[TrainingParagraph]:
    dir = Path(__file__).parent.parent.parent / "data" / "the_monsters_know"
    for file_path in dir.rglob("*.md"):
        text = file_path.read_text(encoding="utf-8")
        name = text.split("\n")[0].replace("#", "").strip()
        paragraphs = split_by_paragraphs(text)
        for p in paragraphs:
            yield TrainingParagraph(topic="mkwtd", name=name, text=p)

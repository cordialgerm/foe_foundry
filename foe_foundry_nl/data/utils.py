import re
from collections.abc import Iterable


def split_markdown_by_headers(text: str) -> Iterable[str]:
    lines = text.split("\n")

    chunks = []
    current_chunk = []
    current_heading = None

    for line in lines:
        if re.match(r"^(##|###) ", line):
            if current_chunk:
                chunks.append((current_heading, "".join(current_chunk)))
                current_chunk = []
            current_heading = line.strip()
        current_chunk.append(line)

    if current_chunk:
        chunks.append((current_heading, "".join(current_chunk)))

    for heading, text in chunks:
        yield f"## {heading}\n\n {text}"


def split_by_paragraphs(text: str) -> Iterable[str]:
    paragraphs = text.split("\n\n")
    for paragraph in paragraphs:
        paragraph = paragraph.strip()
        if not paragraph:
            continue
        yield paragraph


def name_to_key(name: str) -> str:
    key = name.lower()

    prefix = None
    if ", giant" in key:
        key = key.replace(", giant", "")
        prefix = "giant_"

    if key.startswith("npc: "):
        key = key[5:]

    # Remove any text within parentheses
    key = re.sub(r"\s*\(.*?\)\s*", "", key)
    key = (
        key.replace(", ", "_")
        .replace(": ", "_")
        .replace(":", "_")
        .replace("' ", "")
        .replace(",", "_")
        .replace(" ", "_")
        .replace("-", "_")
        .replace("'", "")
        .strip()
    )

    if prefix:
        key = prefix + key

    return key


def list_to_sentence(items: list[str] | list, conjunction="or"):
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    if len(items) == 2:
        return f"{items[0]} {conjunction} {items[1]}"
    return f"{', '.join(items[:-1])}, {conjunction} {items[-1]}"

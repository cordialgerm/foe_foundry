from typing import Any


def fix_punctuation(text: Any) -> Any:
    if not isinstance(text, str):
        return text

    text = text.strip()

    if text.endswith(".."):
        text = text[:-2] + "."

    if text.endswith(" ."):
        text = text[:-2] + "."

    if text.endswith(". ."):
        text = text[:-3] + "."

    if not text.endswith(".") and not text.endswith(">"):
        text = text + "."

    return text

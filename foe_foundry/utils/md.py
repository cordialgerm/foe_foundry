import re


def extract_md_block_from_text(text: str) -> str | None:
    """
    Extracts a markdown block from a given text string.
    """
    matches = re.findall(r"```md(.*?)```", text, re.DOTALL)
    if matches:
        return matches[0].strip()

    return None


def extract_md_blocks_from_text(text: str) -> list[str]:
    """
    Extracts all markdown blocks from a given text string.
    Returns a list of markdown block contents (without the ```md ... ``` wrappers).
    """
    matches = re.findall(r"```md(.*?)```", text, re.DOTALL)
    return [m.strip() for m in matches] if matches else []

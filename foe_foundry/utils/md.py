import re


def extract_md_block_from_text(text: str) -> str | None:
    """
    Extracts a markdown block from a given text string.
    """
    matches = re.findall(r"```md(.*?)```", text, re.DOTALL)
    if matches:
        return matches[0].strip()

    return None

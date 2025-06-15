import re

import yaml


def extract_tagline(markdown_text: str) -> str | None:
    """
    Extracts the tagline (italicized subtitle) from a markdown monster file.
    Looks for a line after the top-level heading that is surrounded by asterisks.

    Args:
        markdown_text (str): Full content of the markdown file.

    Returns:
        str | None: The extracted tagline without asterisks, or None if not found.
    """
    # Split the file into lines
    lines = [l for l in markdown_text.strip().splitlines() if len(l)]

    # Search for the first h1 header and tagline immediately after
    for i, line in enumerate(lines):
        if re.match(r"^#\s", line):  # Header line (e.g., "# Ghoul")
            # Check if next line is a tagline (markdown italic style)
            if i + 1 < len(lines):
                tagline_line = lines[i + 1].strip()
                match = re.match(r"^\*(.+?)\*$", tagline_line)
                if match:
                    return match.group(1)

    return None


def strip_yaml_frontmatter(markdown_text: str) -> str:
    """
    Removes YAML frontmatter from the beginning of a markdown file,
    even if there's leading whitespace or blank lines.

    Args:
        markdown_text (str): The full content of the markdown file.

    Returns:
        str: The markdown content with the YAML frontmatter removed.
    """
    # Remove leading whitespace and blank lines
    trimmed_text = markdown_text.lstrip()

    # Match frontmatter starting with '---' and ending with the next '---'
    match = re.match(r"^---\s*\n.*?\n---\s*\n?", trimmed_text, re.DOTALL)
    if match:
        return trimmed_text[match.end() :]
    return trimmed_text


def extract_yaml_frontmatter(markdown_text: str) -> dict:
    """
    Extracts and parses YAML frontmatter from the beginning of a markdown file.

    Args:
        markdown_text (str): The full content of the markdown file.

    Returns:
        dict: Parsed YAML frontmatter as a dictionary. Returns an empty dict if not found.
    """
    # Remove leading whitespace and blank lines
    trimmed_text = markdown_text.lstrip()

    # Match frontmatter from first '---' to the next '---'
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n?", trimmed_text, re.DOTALL)
    if match:
        yaml_block = match.group(1)
        try:
            return yaml.safe_load(yaml_block) or {}
        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing YAML frontmatter: {e}")
    return {}

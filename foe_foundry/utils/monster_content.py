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
    lines = [line for line in markdown_text.strip().splitlines() if len(line)]

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


def extract_overview_content(markdown_text: str) -> str | None:
    """
    Extracts the overview content from a monster markdown file.

    This includes all markdown content after the tagline and until the tactics section.
    It consists of initial introductory paragraphs describing the monster, and up to
    one additional paragraph that's part of a ## Lore section.

    Strips out markdown image directives and "info" style directives that look like !!!.

    Args:
        markdown_text (str): Full content of the markdown file.

    Returns:
        str | None: The extracted overview content, or None if not found.
    """
    # First strip YAML frontmatter
    content = strip_yaml_frontmatter(markdown_text)
    lines = [line for line in content.strip().splitlines()]

    # Find the tagline end (line after h1 header with italic formatting)
    lore_start_idx = None
    for i, line in enumerate(lines):
        if re.match(r"^#\s", line):  # Header line (e.g., "# Ghoul")
            # Look for tagline in the next few lines (skip empty lines)
            for j in range(i + 1, min(i + 5, len(lines))):
                tagline_line = lines[j].strip()
                if tagline_line and re.match(r"^\*(.+?)\*$", tagline_line):
                    lore_start_idx = j + 1  # Start after tagline
                    break
            if lore_start_idx is not None:
                break

    if lore_start_idx is None:
        return None

    # Find the end of lore content (before tactics section or statblocks section)
    lore_end_idx = None
    for i in range(lore_start_idx, len(lines)):
        line = lines[i].strip()
        # Stop at tactics section, statblocks section, or horizontal rules
        if re.match(r"^##\s+.*[Tt]actics", line):
            lore_end_idx = i
            break
        elif re.match(r"^##\s+.*[Ss]tatblocks?", line):
            lore_end_idx = i
            break
        elif line.startswith("---") and len(line.strip()) >= 3:
            lore_end_idx = i
            break

    if lore_end_idx is None:
        lore_end_idx = len(lines)

    # Extract lore lines
    lore_lines = lines[lore_start_idx:lore_end_idx]

    # Filter out image directives and info-style directives
    filtered_lines = []
    in_info_block = False

    for line in lore_lines:
        # Skip image directives
        if re.match(r"^!\[.*\]\(.*\)", line) or re.match(r"^!\[.*\]\(.*\)\{.*\}", line):
            continue

        # Skip jump/navigation links like "- [Jump...]"
        if re.match(r"^\s*-\s*\[Jump", line.strip()):
            continue

        # Handle info-style directives (starting with !!!)
        if line.strip().startswith("!!!"):
            in_info_block = True
            continue

        # Skip indented content that's part of an info block
        if in_info_block:
            if line.startswith("    ") or line.strip() == "":
                continue
            else:
                # End of info block
                in_info_block = False

        filtered_lines.append(line)

    # Join and clean up the content
    lore_content = "\n".join(filtered_lines).strip()

    return lore_content if lore_content else None


def extract_encounters_content(markdown_text: str) -> str | None:
    """
    Extracts the encounters content from a monster markdown file.

    This includes two markdown paragraphs with corresponding h2 or h3 sections,
    labelled something like "## ... Encounter Ideas" and "## ... Adventure Ideas".

    Args:
        markdown_text (str): Full content of the markdown file.

    Returns:
        str | None: The extracted encounters content, or None if not found.
    """
    # First strip YAML frontmatter
    content = strip_yaml_frontmatter(markdown_text)
    lines = [line for line in content.strip().splitlines()]

    encounters_lines = []
    in_encounters_section = False

    for line in lines:
        stripped_line = line.strip()

        # Check if this is an encounter-related h2 or h3 section
        if (
            re.match(r"^###?\s+.*[Ee]ncounter.*[Ii]deas?", stripped_line)
            or re.match(r"^###?\s+.*[Aa]dventure.*[Ii]deas?", stripped_line)
            or re.match(r"^###?\s+.*[Ee]ncounters?", stripped_line)
            or re.match(r"^###?\s+.*[Aa]dventures?", stripped_line)
        ):
            in_encounters_section = True
            encounters_lines.append(line)
            continue

        # Stop if we hit another h2/h3 section that's not encounters-related
        if re.match(r"^###?\s+", stripped_line) and in_encounters_section:
            # Check if this is still an encounters-related section
            if not (
                re.match(r"^###?\s+.*[Ee]ncounter.*[Ii]deas?", stripped_line)
                or re.match(r"^###?\s+.*[Aa]dventure.*[Ii]deas?", stripped_line)
                or re.match(r"^###?\s+.*[Ee]ncounters?", stripped_line)
                or re.match(r"^###?\s+.*[Aa]dventures?", stripped_line)
            ):
                break
            else:
                encounters_lines.append(line)
                continue

        # Add content if we're in an encounters section
        if in_encounters_section:
            encounters_lines.append(line)

    # Filter out non-header, non-bullet content (like SEO paragraphs)
    filtered_encounters_lines = []
    for line in encounters_lines:
        stripped_line = line.strip()

        # Keep headers (h2/h3)
        if re.match(r"^###?\s+", stripped_line):
            filtered_encounters_lines.append(line)
        # Keep bullet points and list items
        elif re.match(r"^\s*[-*+]\s+", line) or re.match(r"^\s*\d+\.\s+", line):
            filtered_encounters_lines.append(line)
        # Keep empty lines for formatting
        elif stripped_line == "":
            filtered_encounters_lines.append(line)
        # Skip everything else (SEO paragraphs, etc.)

    # Join and clean up the content
    encounters_content = "\n".join(filtered_encounters_lines).strip()

    return encounters_content if encounters_content else None

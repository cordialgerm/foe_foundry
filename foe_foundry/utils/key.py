import re


def name_to_key(name: str) -> str:
    """Convert a monster name to a standardized key format."""

    name = strip_group_qualifier(name)
    return (
        name.lower()
        .strip()
        .replace(" ", "-")
        .replace("_", "-")
        .replace("/", "-")
        .replace("'", "")
        .replace("’", "")  # looks like ' but isnt: ’
        .replace("(", "")
        .replace(")", "")
    )


def strip_group_qualifier(name: str) -> str:
    """Remove trailing (Group) qualifiers from names."""
    return re.sub(r"\s*\([^)]+\)$", "", name)

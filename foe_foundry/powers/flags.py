from ..utils import name_to_key


def theme_flag(theme: str) -> str:
    theme_key = name_to_key(theme)
    return f"theme: {theme_key}"


MODIFIES_CRITICAL = "modifies-critical"

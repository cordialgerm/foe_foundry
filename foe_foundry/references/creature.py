from ..utils import name_to_key


def creature_ref(creature_name: str) -> str:
    key = name_to_key(creature_name)
    return f"<span class='creature creature-{key}>{creature_name}</span>"

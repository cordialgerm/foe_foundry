from ..utils import name_to_key


def creature_ref(creature_name: str) -> str:
    if creature_name.startswith("*") and creature_name.endswith("*"):
        creature_name = creature_name[1:-1]

    key = name_to_key(creature_name)
    return f"<span class='creature creature-{key}'>{creature_name}</span>"

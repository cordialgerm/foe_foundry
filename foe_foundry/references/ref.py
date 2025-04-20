from ..utils import name_to_key


def creature_ref(creature_name: str) -> str:
    if creature_name.startswith("*") and creature_name.endswith("*"):
        creature_name = creature_name[1:-1]

    key = name_to_key(creature_name)
    return f"<span class='creature creature-{key}'>{creature_name}</span>"


def feature_ref(feature_name: str) -> str:
    key = name_to_key(feature_name)
    return f"<span class='feature feature-{key}'>{feature_name}</span>"


def action_ref(action_name: str) -> str:
    key = name_to_key(action_name)
    return f"<span class='action action-{key}'>{action_name}</span>"


def spell_ref(spell_name: str) -> str:
    key = name_to_key(spell_name)
    return f"<span class='spell spell-{key}'>{spell_name}</span>"

from typing import Dict, List, TypeAlias

from ..attack_template import AttackTemplate
from ..statblocks import BaseStatblock
from .scores import HIGH_AFFINITY

AttackName: TypeAlias = str | AttackTemplate
AttackModifiers: TypeAlias = Dict[AttackName, float] | AttackName | List[AttackName] | None


def resolve_attack_modifier(
    candidate: BaseStatblock, attack_modifiers: AttackModifiers
) -> float:
    def simplify(a: AttackName) -> str:
        return a if isinstance(a, str) else a.attack_name

    if not attack_modifiers:
        return 0

    if isinstance(attack_modifiers, list):
        mods = {simplify(a): HIGH_AFFINITY for a in attack_modifiers}
    elif isinstance(attack_modifiers, AttackName):
        mods = {simplify(attack_modifiers): HIGH_AFFINITY}
    elif isinstance(attack_modifiers, dict):
        mods = {simplify(a): s for a, s in attack_modifiers.items()}

    default_modifier = mods.get("*", 0)
    modifier = mods.get(candidate.attack.name, default_modifier)
    return modifier

from typing import List, Set, TypeVar

from ..attributes import Stats
from ..creature_types import CreatureType
from ..damage import DamageType
from ..features import Feature
from ..role_types import MonsterRole
from ..statblocks import BaseStatblock
from .attack import relevant_damage_types
from .attack_modifiers import AttackModifiers, resolve_attack_modifier
from .scores import MODERATE_AFFINITY, NO_AFFINITY

T = TypeVar("T")


def clean_set(a: T | None | List[T] | Set[T], default: Set[T] | None = None) -> Set[T]:
    if default is None:
        default = set()

    if a is None:
        return default
    elif isinstance(a, list):
        return set(a)
    elif isinstance(a, set):
        return a
    else:
        return {a}


def score(
    candidate: BaseStatblock,
    require_roles: MonsterRole | Set[MonsterRole] | List[MonsterRole] | None = None,
    require_types: CreatureType | Set[CreatureType] | List[CreatureType] | None = None,
    require_damage: DamageType | Set[DamageType] | List[DamageType] | None = None,
    require_stats: Stats | List[Stats] | Set[Stats] | None = None,
    bonus_roles: MonsterRole | Set[MonsterRole] | List[MonsterRole] | None = None,
    bonus_types: CreatureType | Set[CreatureType] | List[CreatureType] | None = None,
    bonus_damage: DamageType | Set[DamageType] | List[DamageType] | None = None,
    bonus_stats: Stats | List[Stats] | Set[Stats] | None = None,
    attack_modifiers: AttackModifiers = None,
    require_no_creature_class: bool = False,
    bonus: float = MODERATE_AFFINITY,
    min_cr: float | None = 3,
) -> float:
    """Standard scoring helper function"""

    require_roles = clean_set(require_roles)
    require_types = clean_set(require_types)
    require_damage = clean_set(require_damage)
    require_stats = clean_set(require_stats)
    bonus_roles = clean_set(bonus_roles, require_roles)
    bonus_types = clean_set(bonus_types, require_types)
    bonus_damage = clean_set(bonus_damage, require_damage)
    bonus_stats = clean_set(bonus_stats, default=require_stats)

    candidate_damage_types = relevant_damage_types(candidate)

    if require_no_creature_class and candidate.creature_class is not None:
        return NO_AFFINITY

    if min_cr and candidate.cr < min_cr:
        return NO_AFFINITY

    if require_roles and not candidate.role in require_roles:
        return NO_AFFINITY

    if require_types and not candidate.creature_type in require_types:
        return NO_AFFINITY

    if require_damage and not any(candidate_damage_types.intersection(require_damage)):
        return NO_AFFINITY

    for stat in require_stats:
        if candidate.attributes.stat(stat) < 10:
            return NO_AFFINITY

    score = resolve_attack_modifier(candidate, attack_modifiers)

    if candidate.creature_type in bonus_types:
        score += bonus

    if candidate.role in bonus_roles:
        score += bonus

    if any(candidate_damage_types.intersection(bonus_damage)):
        score += bonus

    for stat in bonus_stats:
        if candidate.attributes.stat(stat) >= 14:
            score += bonus

    return score

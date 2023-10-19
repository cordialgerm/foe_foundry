from typing import Callable, List, Set, TypeAlias, TypeVar

from ..attributes import Skills, Stats
from ..creature_types import CreatureType
from ..damage import AttackType, DamageType
from ..role_types import MonsterRole
from ..size import Size
from ..statblocks import BaseStatblock
from .attack import relevant_damage_types
from .attack_modifiers import AttackModifiers, resolve_attack_modifier
from .scores import MODERATE_AFFINITY, NO_AFFINITY

T = TypeVar("T")
StatblockFilter: TypeAlias = Callable[[BaseStatblock], bool]


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
    require_size: Size | None = None,
    require_speed: int | None = None,
    require_attack_types: AttackType | Set[AttackType] | List[AttackType] | None = None,
    require_skills: Skills | Set[Skills] | List[Skills] | None = None,
    require_no_creature_class: bool = False,
    require_no_other_damage_type: bool = False,
    require_cr: float | None = None,
    require_shield: bool = False,
    require_callback: StatblockFilter | None = None,
    bonus_roles: MonsterRole | Set[MonsterRole] | List[MonsterRole] | None = None,
    bonus_types: CreatureType | Set[CreatureType] | List[CreatureType] | None = None,
    bonus_damage: DamageType | Set[DamageType] | List[DamageType] | None = None,
    bonus_stats: Stats | List[Stats] | Set[Stats] | None = None,
    bonus_size: Size | None = None,
    bonus_speed: int | None = None,
    bonus_attack_types: AttackType | Set[AttackType] | List[AttackType] | None = None,
    bonus_skills: Skills | Set[Skills] | List[Skills] | None = None,
    bonus_cr: float | None = None,
    bonus_shield: bool = False,
    bonus_callback: StatblockFilter | None = None,
    attack_modifiers: AttackModifiers = None,
    stat_threshold: int = 12,
) -> float:
    """Standard scoring helper function"""

    # cleanup parameters
    require_roles = clean_set(require_roles)
    require_types = clean_set(require_types)
    require_damage = clean_set(require_damage)
    require_stats = clean_set(require_stats)
    require_attack_types = clean_set(require_attack_types)
    require_skills = clean_set(require_skills)
    bonus_roles = clean_set(bonus_roles, require_roles)
    bonus_types = clean_set(bonus_types, require_types)
    bonus_damage = clean_set(bonus_damage, require_damage)
    bonus_stats = clean_set(bonus_stats, default=require_stats)
    bonus_attack_types = clean_set(bonus_attack_types, require_attack_types)
    bonus_skills = clean_set(bonus_skills, require_skills)

    candidate_damage_types = relevant_damage_types(candidate)
    bonus_size = bonus_size or require_size
    bonus_speed = bonus_speed or require_speed
    bonus_callback = bonus_callback or require_callback
    bonus_cr = bonus_cr or require_cr
    bonus_shield = bonus_shield or require_shield

    # checks against required
    if require_no_creature_class and candidate.creature_class is not None:
        return NO_AFFINITY

    if require_cr and candidate.cr < require_cr:
        return NO_AFFINITY

    if require_size is not None and candidate.size < require_size:
        return NO_AFFINITY

    if require_speed is not None and candidate.speed.fastest_speed < require_speed:
        return NO_AFFINITY

    if require_roles and not candidate.role in require_roles:
        return NO_AFFINITY

    if require_types and not candidate.creature_type in require_types:
        return NO_AFFINITY

    if require_damage and not any(candidate_damage_types.intersection(require_damage)):
        return NO_AFFINITY

    if require_attack_types and not candidate.attack_type in require_attack_types:
        return NO_AFFINITY

    if require_skills and not all(
        candidate.attributes.has_proficiency_or_expertise(s) for s in require_skills
    ):
        return NO_AFFINITY

    for stat in require_stats:
        if candidate.attributes.stat(stat) < stat_threshold:
            return NO_AFFINITY

    if (
        require_no_other_damage_type
        and bonus_damage
        and candidate.secondary_damage_type is not None
        and candidate.secondary_damage_type not in bonus_damage
    ):
        return NO_AFFINITY

    if require_shield and not candidate.uses_shield:
        return NO_AFFINITY

    if require_callback is not None and not require_callback(candidate):
        return NO_AFFINITY

    # bonus checks
    score = resolve_attack_modifier(candidate, attack_modifiers)

    if candidate.creature_type in bonus_types:
        score += MODERATE_AFFINITY

    if candidate.role in bonus_roles:
        score += MODERATE_AFFINITY

    if any(candidate_damage_types.intersection(bonus_damage)):
        score += MODERATE_AFFINITY

    if any(candidate.attributes.has_proficiency_or_expertise(s) for s in bonus_skills):
        score += MODERATE_AFFINITY

    if candidate.attack_type in bonus_attack_types:
        score += MODERATE_AFFINITY

    for stat in bonus_stats:
        if candidate.attributes.stat(stat) >= stat_threshold + 2:
            score += MODERATE_AFFINITY

    if bonus_size is not None and candidate.size >= bonus_size:
        score += MODERATE_AFFINITY

    if bonus_speed is not None and candidate.speed.fastest_speed >= bonus_speed:
        score += MODERATE_AFFINITY

    if bonus_cr and candidate.cr >= bonus_cr:
        score += MODERATE_AFFINITY

    if bonus_shield and candidate.uses_shield:
        score += MODERATE_AFFINITY

    if bonus_callback and bonus_callback(candidate):
        score += MODERATE_AFFINITY

    return score

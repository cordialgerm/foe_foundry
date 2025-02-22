from typing import Callable, List, Set, TypeAlias, TypeVar

from ..attack_template import AttackTemplate
from ..attributes import Skills, Stats
from ..creature_types import CreatureType
from ..damage import AttackType, DamageType
from ..role_types import MonsterRole
from ..size import Size
from ..statblocks import BaseStatblock
from .attack import relevant_damage_types

AttackName: TypeAlias = str | AttackTemplate
AttackNames: TypeAlias = AttackName | List[AttackName] | Set[AttackName] | None

T = TypeVar("T")
StatblockFilter: TypeAlias = Callable[[BaseStatblock], bool]


def _clean_set(a: T | None | List[T] | Set[T]) -> Set[T]:
    if isinstance(a, list):
        return set(a)
    elif isinstance(a, set):
        return a
    elif a is None:
        return set()
    else:
        return {a}


class _RequirementTracker:
    def __init__(self):
        self.require_constraints = 0
        self.bonus_constraints = 0
        self.require_hits = 0
        self.require_misses = 0
        self.bonus_hits = 0
        self.bonus_misses = 0
        self.weight = 1.0

    def required(self, result: bool, weight: float = 1.0):
        if result:
            self.require_hits += 1
            self.weight *= weight
        else:
            self.require_misses += 1

    def bonus(self, result: bool, weight: float = 1.0):
        if result:
            self.bonus_hits += 1
            self.weight *= weight
        else:
            self.bonus_misses += 1

    def require_flag(self, v: bool) -> bool:
        if v:
            self.require_constraints += 1
        return v

    def optional_flag(self, v: bool) -> bool:
        if v:
            self.bonus_constraints += 1
        return v

    def require_val(self, v: T | None) -> T | None:
        if v is not None and v is not False:
            self.require_constraints += 1
        return v  # type: ignore

    def optional_val(self, v: T | None, default: T | None) -> T | None:
        if v is not None:
            self.bonus_constraints += 1
            return v
        else:
            return default

    def require_set(self, a: T | None | List[T] | Set[T]) -> Set[T]:
        clean_set = _clean_set(a)
        if len(clean_set) > 0:
            self.require_constraints += 1
        return clean_set

    def optional_set(self, a: T | None | List[T] | Set[T], default: Set[T]) -> Set[T]:
        clean_set = _clean_set(a)
        if len(clean_set) > 0:
            self.bonus_constraints += 1
            return clean_set
        else:
            return default

    def check_attacks(self, candidate: BaseStatblock, attack_names: AttackNames):
        def simplify(a: AttackName) -> str:
            return a if isinstance(a, str) else a.attack_name

        if attack_names is None:
            attacks: Set[str] = set()
        elif isinstance(attack_names, list):
            attacks = {simplify(a) for a in attack_names}
        elif isinstance(attack_names, AttackName):
            attacks = {simplify(attack_names)}
        else:
            attacks = {simplify(a) for a in attack_names}

        attack_in_list = candidate.attack.name in attacks

        if len(attacks) == 0:
            return
        elif "-" in attacks:
            self.require_constraints += 1
            self.require_hits += attack_in_list
            self.require_misses += not attack_in_list
        else:
            self.bonus_constraints += 1
            self.bonus_hits += attack_in_list
            self.bonus_misses += not attack_in_list

    @property
    def score(self) -> float:
        if self.require_misses > 0:
            return -1

        score = 1 if self.require_hits >= 1 else 0.5

        # if there are many required checks and you pass them all then you should get a score boost
        # this is because narrowly defined powers are unique and interesting, so if a candidate qualifies they should have a boosted chance
        strict_requirement_boost = 0.1 * min(max(0, self.require_hits - 2), 3)

        # get a score boost for bonus checks
        bonus_boost = 0.1 * min(self.bonus_hits, 3)

        final_score = self.weight * (score + strict_requirement_boost + bonus_boost)
        return final_score


def score(
    *,
    candidate: BaseStatblock,
    relaxed_mode: bool = False,
    require_roles: MonsterRole | Set[MonsterRole] | List[MonsterRole] | None = None,
    require_types: CreatureType | Set[CreatureType] | List[CreatureType] | None = None,
    require_damage: DamageType | Set[DamageType] | List[DamageType] | None = None,
    require_stats: Stats | List[Stats] | Set[Stats] | None = None,
    require_size: Size | None = None,
    require_speed: int | None = None,
    require_flying: bool = False,
    require_swimming: bool = False,
    require_attack_types: AttackType | Set[AttackType] | List[AttackType] | None = None,
    require_skills: Skills | Set[Skills] | List[Skills] | None = None,
    require_no_creature_class: bool = False,
    require_damage_exact_match: bool = False,
    require_secondary_damage_type: bool = False,
    require_cr: float | None = None,
    require_max_cr: float | None = None,
    require_shield: bool = False,
    require_callback: StatblockFilter | None = None,
    bonus_roles: MonsterRole | Set[MonsterRole] | List[MonsterRole] | None = None,
    bonus_types: CreatureType | Set[CreatureType] | List[CreatureType] | None = None,
    bonus_damage: DamageType | Set[DamageType] | List[DamageType] | None = None,
    bonus_stats: Stats | List[Stats] | Set[Stats] | None = None,
    bonus_size: Size | None = None,
    bonus_speed: int | None = None,
    bonus_flying: bool = False,
    bonus_swimming: bool = False,
    bonus_attack_types: AttackType | Set[AttackType] | List[AttackType] | None = None,
    bonus_skills: Skills | Set[Skills] | List[Skills] | None = None,
    bonus_cr: float | None = None,
    bonus_max_cr: float | None = None,
    bonus_shield: bool = False,
    bonus_callback: StatblockFilter | None = None,
    attack_names: AttackNames = None,
    stat_threshold: int = 12,
    score_multiplier: float = 1.0,
) -> float:
    """Standard scoring helper function"""

    candidate_damage_types = relevant_damage_types(candidate)

    # cleanup parameters
    t = _RequirementTracker()
    require_roles = t.require_set(require_roles)
    require_types = t.require_set(require_types)
    require_damage = t.require_set(require_damage)
    require_stats = t.require_set(require_stats)
    require_size = t.require_val(require_size)
    require_speed = t.require_val(require_speed)
    require_attack_types = t.require_set(require_attack_types)
    require_skills = t.require_set(require_skills)
    require_no_creature_class = t.require_flag(require_no_creature_class)
    require_cr = t.require_val(require_cr)
    require_max_cr = t.require_val(require_max_cr)
    require_shield = t.require_flag(require_shield)
    require_callback = t.require_val(require_callback)

    bonus_roles = t.optional_set(bonus_roles, require_roles)
    bonus_types = t.optional_set(bonus_types, require_types)
    bonus_damage = t.optional_set(bonus_damage, require_damage)
    bonus_stats = t.optional_set(bonus_stats, default=require_stats)
    bonus_size = t.optional_val(bonus_size, require_size)
    bonus_speed = t.optional_val(bonus_speed, require_speed)
    bonus_attack_types = t.optional_set(bonus_attack_types, require_attack_types)
    bonus_skills = t.optional_set(bonus_skills, require_skills)
    bonus_cr = t.optional_val(bonus_cr, require_cr)
    bonus_max_cr = t.optional_val(bonus_max_cr, require_max_cr)
    bonus_shield = t.optional_flag(require_shield)
    bonus_callback = t.optional_val(bonus_callback, require_callback)

    # checks against required conditions
    if require_roles:
        has_main_role = candidate.role in require_roles
        has_additional_role = any(
            c in require_roles for c in candidate.additional_roles
        )
        if has_main_role:
            t.required(True)
        elif has_additional_role:
            t.required(True, weight=0.75)  # additional roles are less important
        else:
            t.required(False)

    if require_types:
        t.required(candidate.creature_type in require_types or relaxed_mode)

    if require_damage:
        t.required(
            any(candidate_damage_types.intersection(require_damage)) or relaxed_mode
        )

    if require_stats:
        t.required(
            all(candidate.attributes.stat(s) >= stat_threshold for s in require_stats)
            or relaxed_mode
        )

    if require_size:
        t.required(candidate.size >= require_size or relaxed_mode)

    if require_speed:
        t.required(candidate.speed.fastest_speed >= require_speed or relaxed_mode)

    if require_flying:
        t.required((candidate.speed.fly or 0) > 0)

    if require_swimming:
        t.required((candidate.speed.swim or 0) > 0)

    if require_attack_types:
        has_required_attack_type = (
            len(candidate.attack_types.intersection(require_attack_types)) > 0
        )
        t.required(has_required_attack_type)

    if require_skills:
        t.required(
            any(
                candidate.attributes.has_proficiency_or_expertise(s)
                for s in require_skills
            )
        )

    if require_no_creature_class:
        t.required(candidate.creature_class is None or relaxed_mode)

    if require_cr:
        t.required(candidate.cr >= require_cr)

    if require_max_cr:
        t.required(candidate.cr <= require_max_cr)

    if require_shield:
        t.required(candidate.uses_shield)

    if require_callback is not None:
        t.required(require_callback(candidate) or relaxed_mode)

    if require_damage_exact_match:
        resolved_damage_types = require_damage | bonus_damage
        t.required(
            candidate.primary_damage_type in resolved_damage_types
            or candidate.secondary_damage_type in resolved_damage_types
            or relaxed_mode
        )

    if require_secondary_damage_type:
        t.required(candidate.secondary_damage_type is not None)

    # checks against attacks
    t.check_attacks(candidate, attack_names)

    # checks against bonus conditions
    if bonus_types:
        t.bonus(candidate.creature_type in bonus_types)

    if bonus_roles:
        has_main_role = candidate.role in bonus_roles
        has_additional_role = any(c in bonus_roles for c in candidate.additional_roles)

        if has_main_role:
            t.bonus(True)
        elif has_additional_role:
            t.bonus(True, weight=0.75)  # additional roles are less important
        else:
            t.bonus(False)

    if bonus_damage:
        t.bonus(any(candidate_damage_types.intersection(bonus_damage)))

    if bonus_skills:
        t.bonus(
            any(
                candidate.attributes.has_proficiency_or_expertise(s)
                for s in bonus_skills
            )
        )

    if bonus_attack_types:
        has_required_attack_type = (
            len(candidate.attack_types.intersection(bonus_attack_types)) > 0
        )
        t.bonus(has_required_attack_type)

    if bonus_stats:
        t.bonus(
            any(
                candidate.attributes.stat(stat) >= stat_threshold + 2
                for stat in bonus_stats
            )
        )

    if bonus_size:
        t.bonus(candidate.size >= bonus_size)

    if bonus_speed:
        t.bonus(candidate.speed.fastest_speed >= bonus_speed)

    if bonus_flying:
        t.bonus((candidate.speed.fly or 0) > 0)

    if bonus_swimming:
        t.bonus((candidate.speed.swim or 0) > 0)

    if bonus_cr:
        t.bonus(candidate.cr >= bonus_cr)

    if bonus_max_cr:
        t.bonus(candidate.cr <= bonus_max_cr)

    if bonus_shield:
        t.bonus(candidate.uses_shield)

    if bonus_callback:
        t.bonus(bonus_callback(candidate))

    return t.score * score_multiplier

from math import ceil
from typing import List, Set, Tuple

import numpy as np

from ..attributes import Skills, Stats
from ..creature_types import CreatureType
from ..damage import Condition, Damage, DamageType
from ..die import DieFormula
from ..features import ActionType, Feature
from ..role_types import MonsterRole
from ..size import Size
from ..statblocks import BaseStatblock


def flavorful_damage_types(
    candidate: BaseStatblock, default: DamageType | None = None
) -> Set[DamageType]:
    """Creates some flavorful options for secondary damage types that a candidate might employ"""

    if candidate.secondary_damage_type is not None:
        return {candidate.secondary_damage_type}

    creature_type = candidate.creature_type
    role = candidate.role

    # ensure options are unique
    options = set()

    # check creature type
    if creature_type == CreatureType.Aberration:
        options.add(DamageType.Psychic)
    elif creature_type == CreatureType.Beast:
        pass  # look at role
    elif creature_type == CreatureType.Celestial:
        options.add(DamageType.Radiant)
    elif creature_type == CreatureType.Construct:
        options.update(
            [DamageType.Fire, DamageType.Cold, DamageType.Acid, DamageType.Lightning]
        )
    elif creature_type == CreatureType.Dragon:
        options.update(
            [
                DamageType.Fire,
                DamageType.Cold,
                DamageType.Acid,
                DamageType.Poison,
                DamageType.Lightning,
            ]
        )
    elif creature_type == CreatureType.Elemental:
        options.update([DamageType.Fire, DamageType.Cold, DamageType.Lightning])
    elif creature_type == CreatureType.Fey:
        options.update([DamageType.Poison, DamageType.Psychic])
    elif creature_type == CreatureType.Fiend:
        options.add(DamageType.Fire)
    elif creature_type == CreatureType.Giant:
        options.update([DamageType.Fire, DamageType.Cold])
    elif creature_type == CreatureType.Humanoid:
        pass  # look at role
    elif creature_type == CreatureType.Monstrosity:
        pass  # look at role
    elif creature_type == CreatureType.Undead:
        options.add(DamageType.Necrotic)
    elif creature_type == CreatureType.Ooze:
        options.add(DamageType.Acid)
    elif creature_type == CreatureType.Plant:
        options.add(DamageType.Poison)

    # check roles
    if role == MonsterRole.Ambusher:
        options.add(DamageType.Poison)
    elif role == MonsterRole.Artillery:
        options.update([DamageType.Fire, DamageType.Lightning, DamageType.Cold])
    elif role == MonsterRole.Bruiser:
        pass
    elif role == MonsterRole.Controller:
        options.add(DamageType.Psychic)
    elif role == MonsterRole.Defender:
        pass
    elif role == MonsterRole.Leader:
        options.add(DamageType.Poison)
    elif role == MonsterRole.Skirmisher:
        options.add(DamageType.Poison)

    # handle default
    if len(options) == 0 and default is not None:
        options = {default}

    return options


def relevant_damage_types(candidate: BaseStatblock):
    damage_types = flavorful_damage_types(candidate)
    if candidate.secondary_damage_type:
        damage_types.add(candidate.secondary_damage_type)
    damage_types.add(candidate.primary_damage_type)
    return damage_types

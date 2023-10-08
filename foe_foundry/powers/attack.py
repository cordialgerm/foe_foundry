from math import ceil
from typing import List, Set, Tuple

import numpy as np

from foe_foundry.features import Feature
from foe_foundry.statblocks import BaseStatblock

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

    if default is None:
        default = candidate.secondary_damage_type

    creature_type, role = candidate.creature_type, candidate.role

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


def flavorful_debilitating_conditions(
    candidate: BaseStatblock, default: Condition | None = None
) -> Set[Condition]:
    damage_types = flavorful_damage_types(candidate)

    options = set()

    if DamageType.Acid in damage_types:
        options.add(Condition.Blinded)

    if DamageType.Cold in damage_types:
        options.add(Condition.Stunned)

    if DamageType.Fire in damage_types:
        options.add(Condition.Blinded)

    if DamageType.Lightning in damage_types:
        options.add(Condition.Stunned)

    if DamageType.Necrotic in damage_types:
        options.add(Condition.Poisoned)

    if DamageType.Poison in damage_types:
        options.add(Condition.Poisoned)

    if DamageType.Psychic in damage_types:
        options.update([Condition.Frightened, Condition.Charmed])

    if DamageType.Radiant in damage_types:
        options.update([Condition.Frightened, Condition.Blinded])

    if DamageType.Thunder in damage_types:
        options.update(Condition.Deafened)

    # Large creatures can knock you prone
    if (
        candidate.size >= Size.Large
        or candidate.creature_type == CreatureType.Giant
        or candidate.attributes.has_proficiency_or_expertise(Skills.Athletics)
        or candidate.attributes.STR >= 18
    ):
        options.add(Condition.Prone)

    # Huge creatures can stun you
    if candidate.size >= Size.Huge and candidate.primary_attribute == Stats.STR:
        options.add(Condition.Prone)

    if len(options) == 0 and default is None:
        options.add(default)

    return options


def secondary_damage_attack(
    stats: BaseStatblock, damage_type: DamageType
) -> Tuple[BaseStatblock, Feature]:
    if damage_type == DamageType.Acid:
        name = "Corrosive Attacks"
    elif damage_type == DamageType.Cold:
        name = "Chilling Attacks"
    elif damage_type == DamageType.Fire:
        name = "Superheated Attacks"
    elif damage_type == DamageType.Force:
        name = "Energetic Attacks"
    elif damage_type == DamageType.Lightning:
        name = "Electrified Attacks"
    elif damage_type == DamageType.Necrotic:
        name = "Draining Attacks"
    elif damage_type == DamageType.Poison:
        name = "Poisoned Attacks"
    elif damage_type == DamageType.Psychic:
        name = "Unsettling Attacks"
    elif damage_type == DamageType.Radiant:
        name = "Divine Smite"
    else:
        name = "Damaging Attack"

    dmg = int(ceil(stats.cr))

    feature = Feature(
        name=name,
        description=f"This creature's attacks deal an extra {dmg} {damage_type} damage (included in the attack)",
        action=ActionType.Feature,
        hidden=True,
    )

    additional_damage = Damage(
        formula=DieFormula.from_expression(f"{dmg}"), damage_type=damage_type
    )
    new_attack = stats.attack.copy(additional_damage=additional_damage)

    stats = stats.copy(secondary_damage_attack=damage_type, attack=new_attack)
    return stats, feature


def debilitating_attack(
    stats: BaseStatblock, condition: Condition, save: Stats | None = None
) -> Tuple[BaseStatblock, Feature]:
    condition_str = None
    if condition == Condition.Blinded:
        name = "Blinding Attacks"
    elif condition == Condition.Charmed:
        name = "Confusing Attacks"
    elif condition == Condition.Deafened:
        name = "Deafening Attacks"
    elif condition == Condition.Exhaustion:
        name = "Exhausting Attacks"
        condition_str = "gains one level of Exhaustion"
    elif condition == Condition.Frightened:
        name = "Frightening Attacks"
    elif condition == Condition.Grappled:
        name = "Grappling Attacks"
    elif condition == Condition.Incapacitated:
        name = "Incapacitating Attacks"
    elif condition == Condition.Paralyzed:
        name = "Paralyzing Attacks"
    elif condition == Condition.Petrified:
        name = "Petrifying Attacks"
    elif condition == Condition.Poisoned:
        name = "Poisoning Attacks"
    elif condition == Condition.Prone:
        name = "Trip Attack"
    elif condition == Condition.Restrained:
        name = "Restraining Strike"
    elif condition == Condition.Stunned:
        name = "Stunning Strike"
    elif condition == Condition.Unconscious:
        name = "Sleep Attack"
    else:
        raise ValueError(f"Unsupported condition: {condition}")

    if condition_str is None:
        condition_str = f"becomes {condition}"

    if save is None:
        condition_str += " until the end of its next turn."
    else:
        dc = stats.difficulty_class
        condition_str += (
            f" unless it succeeds on a DC {dc} {save} save (save ends at end of turn)"
        )

    feature = Feature(
        name=name,
        action=ActionType.Feature,
        description=f"On a hit, the target {condition_str}",
        modifies_attack=True,
        hidden=True,
    )

    return stats, feature

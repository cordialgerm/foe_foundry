from math import ceil
from typing import List, Tuple

from foe_foundry.features import Feature
from foe_foundry.statblocks import BaseStatblock

from ..damage import AttackType, Damage, DamageType
from ..die import DieFormula
from ..features import ActionType, Feature
from ..role_types import MonsterRole
from ..statblocks import BaseStatblock
from .power import Power, PowerType
from .scores import (
    EXTRA_HIGH_AFFINITY,
    HIGH_AFFINITY,
    LOW_AFFINITY,
    MODERATE_AFFINITY,
    NO_AFFINITY,
)


class _DamagingAttack(Power):
    """This creature's attacks deal an extra CR damage of a type appropriate for the creature."""

    def __init__(self):
        super().__init__(name="Damaging Attack", power_type=PowerType.Common)

    def score(self, candidate: BaseStatblock) -> float:
        # this power can make sense for any monster
        # monsters that use a dedicated weapon or already have a secondary damage type assigned are preferred slightly
        # ambushers get a boost to this as well

        score = MODERATE_AFFINITY

        if candidate.attack_type in {AttackType.MeleeWeapon, AttackType.RangedWeapon}:
            score += LOW_AFFINITY
        if candidate.secondary_damage_type is not None:
            score += LOW_AFFINITY
        if candidate.role == MonsterRole.Ambusher:
            score += LOW_AFFINITY

        return score

    def apply(self, stats: BaseStatblock) -> Tuple[BaseStatblock, Feature]:
        damage_type = stats.secondary_damage_type

        # if the monster doesn't already have a damage type, use poison
        if damage_type is None:
            damage_type = DamageType.Poison
            stats = stats.copy(secondary_damage_type=damage_type)

        # TODO - integrate this directly into the Attack
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
            description=f"This creature's attacks deal an extra {dmg} {damage_type} damage",
            action=ActionType.Feature,
        )

        additional_damage = Damage(
            formula=DieFormula.from_expression(f"{dmg}"), damage_type=damage_type
        )
        new_attack = stats.attack.copy(additional_damage=additional_damage)
        new_stats = stats.copy(attack=new_attack)

        return new_stats, feature


DamagingAttack: Power = _DamagingAttack()

AttackPowers: List[Power] = [DamagingAttack]

# TODO - enhance the Attack class so there can be multiple attacks
# TODO - enhance the Attack class so there can be an effect if all attacks hit
# TODO - organize these
# Grappling Claw Attacks (Chuul)
# Grappling Tentacle Attacks (see above)
# Stinging Poison (Chuul, Wyvern, etc.)
# Bite
# Fist
# Axe
# Club
# Spear
# Horn
# Tail
# Constrict
# Hooves

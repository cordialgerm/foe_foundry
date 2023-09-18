from math import ceil
from typing import List, Tuple

import numpy as np
from numpy.random import Generator

from foe_foundry.die import DieFormula
from foe_foundry.features import Feature
from foe_foundry.powers.power_type import PowerType
from foe_foundry.statblocks import BaseStatblock

from ...attributes import Skills, Stats
from ...creature_types import CreatureType
from ...damage import AttackType, Burning, DamageType, Dazed, Frozen, Shocked
from ...features import ActionType, Feature
from ...statblocks import BaseStatblock, MonsterDials
from ..attack import flavorful_damage_types
from ..power import Power, PowerType
from ..scores import (
    EXTRA_HIGH_AFFINITY,
    HIGH_AFFINITY,
    LOW_AFFINITY,
    MODERATE_AFFINITY,
    NO_AFFINITY,
)


def _score(candidate: BaseStatblock) -> float:
    score = 0

    if (
        candidate.secondary_damage_type is not None
        and candidate.secondary_damage_type.is_elemental
    ):
        score += MODERATE_AFFINITY

    if candidate.creature_type == CreatureType.Elemental:
        score += HIGH_AFFINITY

    return score if score > 0 else NO_AFFINITY


def _as_elemental(stats: BaseStatblock) -> BaseStatblock:
    if stats.secondary_damage_type is None or not stats.secondary_damage_type.is_elemental:
        stats = stats.copy(secondary_damage_type=DamageType.Fire)
    return stats


class _DamagingAura(Power):
    """Any creature who moves within 10 feet of this creature or who starts their turn there takes CR damage of a type appropriate for this creature."""

    def __init__(self):
        super().__init__(name="Damaging Aura", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        # this power makes a lot of sense for foes with a secondary damage type
        # it can also make sense for large STR-martials (wielding many weapons)

        if candidate.secondary_damage_type is not None:
            return HIGH_AFFINITY
        else:
            return NO_AFFINITY

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature]:
        if stats.secondary_damage_type is None:
            stats = stats.copy(secondary_damage_type=stats.primary_damage_type)

        damage_type = stats.secondary_damage_type

        if damage_type == DamageType.Acid:
            name = "Corrosive Fumes"
        elif damage_type == DamageType.Bludgeoning:
            name = "Flurry of Blows"
        elif damage_type == DamageType.Cold:
            name = "Arctic Chill"
        elif damage_type == DamageType.Fire:
            name = "Superheated"
        elif damage_type == DamageType.Force:
            name = "Disintegrating Presence"
        elif damage_type == DamageType.Lightning:
            name = "Arcing Electricity"
        elif damage_type == DamageType.Necrotic:
            name = "Deathly Presence"
        elif damage_type == DamageType.Piercing:
            name = "Bristling"
        elif damage_type == DamageType.Poison:
            name = "Toxic Presence"
        elif damage_type == DamageType.Psychic:
            name = "Unsettling Presence"
        elif damage_type == DamageType.Radiant:
            name = "Holy Presence"
        elif damage_type == DamageType.Slashing:
            name = "Constant Slashing"
        else:
            name = "Damaging Aura"

        dmg = int(ceil(stats.cr))

        feature = Feature(
            name=name,
            description=f"Any creature who moves within 10 feet of {stats.selfref} or who starts their turn there takes {dmg} {damage_type} damage",
            action=ActionType.Feature,
        )

        return stats, feature


class _ElementalAffinity(Power):
    """This creature is aligned to a particular element"""

    def __init__(self):
        super().__init__(name="ElementalAffinity", power_type=PowerType.Creature)

    def score(self, candidate: BaseStatblock) -> float:
        # if the monster has a secondary damage type then it's a good fit
        # otherwise, certain monster types are good fits
        score = 0
        if candidate.secondary_damage_type is not None:
            score += MODERATE_AFFINITY
        elif flavorful_damage_types(candidate) is not None:
            score += MODERATE_AFFINITY

        return score if score > 0 else NO_AFFINITY

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature]:
        damage_type = stats.secondary_damage_type

        if damage_type is None:
            candidates = flavorful_damage_types(stats, default=DamageType.Fire)
            i = rng.choice(len(candidates))
            damage_type = list(candidates)[i]
            stats = stats.copy(secondary_damage_type=damage_type)

        if stats.cr <= 8 and damage_type not in stats.damage_resistances:
            new_damage_resistances = stats.damage_resistances.copy() | {damage_type}
            stats = stats.copy(damage_resistances=new_damage_resistances)
            descr = "resistance"
        else:
            new_damage_resistances = stats.damage_resistances.copy() - {damage_type}
            new_damage_immunities = stats.damage_immunities.copy() | {damage_type}
            descr = "immunity"
            stats = stats.copy(
                damage_resistances=new_damage_resistances,
                damage_immunities=new_damage_immunities,
            )

        dmg = damage_type.name.lower()
        feature = Feature(
            name=f"{damage_type.name} Affinity",
            description=f"{stats.selfref.capitalize()} gains {descr} to {dmg} damage. It gains advantage on its attacks while it is in an environment where sources of {dmg} damage are prevalant.",
            action=ActionType.Feature,
        )
        return stats, feature


class _ElementalShroud(Power):
    def __init__(self):
        super().__init__(name="Elemental Shroud", power_type=PowerType.Creature)

    def score(self, candidate: BaseStatblock) -> float:
        return _score(candidate)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        stats = _as_elemental(stats)

        dmg_type = stats.secondary_damage_type or DamageType.Fire
        dmg = int(ceil(5 + stats.cr))

        feature = Feature(
            name="Elemental Shroud",
            description=f"When {stats.selfref} is hit by a melee attack, their body is shrouded with {dmg_type} energy.\
                Until the start of their next turn, any creature who touches {stats.selfref} or hits them with a melee attack takes {dmg} {dmg_type} damage.",
            uses=1,
            action=ActionType.Reaction,
        )

        return stats, feature


class _ElementalBurst(Power):
    def __init__(self):
        super().__init__(name="Elemental Burst", power_type=PowerType.Creature)

    def score(self, candidate: BaseStatblock) -> float:
        return _score(candidate)

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, Feature | List[Feature]]:
        stats = _as_elemental(stats)

        uses = int(ceil(stats.cr / 5))
        dmg_type = stats.secondary_damage_type or DamageType.Fire
        dmg = int(1.25 * ceil(stats.attack.average_damage))
        distance = 5 if stats.cr <= 7 else 10
        dc = stats.difficulty_class
        feature = Feature(
            name="Elemental Burst",
            action=ActionType.Reaction,
            uses=uses,
            description=f"When {stats.selfref} is hit by a melee attack, their form explodes with {dmg_type} energy. \
                Each other creature within {distance} ft must make a DC {dc} Dexterity saving throw, \
                taking {dmg} {dmg_type} damage on a failure and half as much damage on a success.",
        )
        return stats, feature


class _ElementalMagic(Power):
    def __init__(self):
        super().__init__(name="Elemental Magic", power_type=PowerType.Creature)

    def score(self, candidate: BaseStatblock) -> float:
        return _score(candidate)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        stats = _as_elemental(stats)

        dmg_type = stats.secondary_damage_type
        dc = stats.difficulty_class

        if dmg_type == DamageType.Fire:
            name = "Fireball"
            dmg = int(ceil(1.75 * stats.attack.average_damage))
            description = f"{stats.selfref.capitalize()} targets a 20 ft sphere at a point it can see within 150 feet. A fiery explosion fills the space. \
                All creatures within the space must make a DC {dc} Dexterity saving throw, taking {dmg} {dmg_type} damage on a failure and half as much on a success."
        elif dmg_type == DamageType.Acid:
            name = "Acidic Blast"
            dmg = int(ceil(1.25 * stats.attack.average_damage))
            ongoing = int(ceil(dmg / 2))
            description = f"{stats.selfref.capitalize()} targets a 20 ft sphere at a point it can see within 150 feet. A volatile sphere of acid explodes, inundating the space. \
                All creatures within the space must make a DC {dc} Dexterity saving throw. On a failed save, a creature takes {dmg} {dmg_type} damage and becomes coated in acid. \
                While coated in this way, the creature takes {ongoing} ongoing {dmg_type} damage at the end of each of its turns. A creature may use an Action to remove the acid coating. \
                On a success, the creature takes half as much damage and is not coated."
        elif dmg_type == DamageType.Cold:
            name = "Cone of Cold"
            dmg = int(ceil(1.5 * stats.attack.average_damage))
            description = f"{stats.selfref.capitalize()} releases a blast of cold air in a 60 foot cone. Each creature in the area must make a DC {dc} Constitution save, \
                taking {dmg} {dmg_type} damage on a failure and half as much on a success."
        elif dmg_type == DamageType.Lightning:
            name = "Lightning Bolt"
            dmg = int(ceil(1.75 * stats.attack.average_damage))
            description = f"{stats.selfref.capitalize()} releases a crackling bolt of lightning in a 100 ft line that is 5 ft wide. Each creature in the line must make a DC {dc} Dexterity save, \
                taking {dmg} {dmg_type} on a failure and half as much on a success."
        elif dmg_type == DamageType.Poison:
            name = "Poison Cloud"
            dmg = int(ceil(stats.attack.average_damage))
            description = f"{stats.selfref.capitalize()} creates a 20-ft radius cloud of toxic gas centered at a point it can see within 60 feet. Each creature that starts its turn in the cloud \
                must make a DC {dc} Constitution saving throw. On a failure, a creature takes {dmg} {dmg_type} damage and is **Poisoned** until the end of its next turn. On a success, a creature takes half as much damage and is not poisoned."
        elif dmg_type == DamageType.Thunder:
            name = "Thunderwave"
            dmg = int(ceil(1.75 * stats.attack.average_damage))
            description = f"{stats.selfref.capitalize()} releases a burst of thundrous energy in a 15 ft. cube originating from {stats.selfref}. \
                Each creature in the area must make a DC {dc} Constitution saving throw. On a failure, a creature takes {dmg} {dmg_type} thunder damage and is knocked up to 10 feet away and lands **Prone**. \
                On a success, a creature takes half as much damage and is not knocked prone."
        else:
            raise NotImplementedError(f"{dmg_type} is not supported")

        feature = Feature(
            name=name,
            action=ActionType.Action,
            description=description,
            recharge=5,
            replaces_multiattack=2,
        )

        return stats, feature


class _ElementalSmite(Power):
    def __init__(self):
        super().__init__(name="Elemental Smite", power_type=PowerType.Creature)

    def score(self, candidate: BaseStatblock) -> float:
        return _score(candidate)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        stats = _as_elemental(stats)

        dmg_type = stats.secondary_damage_type
        dc = stats.difficulty_class
        dmg = int(ceil(0.5 * stats.attack.average_damage))

        if dmg_type == DamageType.Fire:
            name = "Fiery Smite"
            burning = Burning(DieFormula.from_expression("1d10"))
            condition = f"and forces the target to make a DC {dc} Constitution saving throw. On a failure, the target is {burning.caption}. {burning.description_3rd}"
        elif dmg_type == DamageType.Acid:
            name = "Acidic Smite"
            burning = Burning(DieFormula.from_expression("1d10"), DamageType.Acid)
            condition = f"and forces the target to make a DC {dc} Dexterity saving throw. On a failure, the target is {burning.caption}. {burning.description_3rd}"
        elif dmg_type == DamageType.Cold:
            name = "Chill Smite"
            frozen = Frozen(dc=dc)
            condition = f"and forces the target to make a DC {dc} Constitution saving throw. On a failure, the target is {frozen.caption}. {frozen.description_3rd}"
        elif dmg_type == DamageType.Lightning:
            name = "Shocking Smite"
            shocked = Shocked()
            condition = f"and forces the target to make a DC {dc} Dexterity saving throw. On a failure, the target is {shocked.caption} until the end of its next turn. {shocked.description_3rd}"
        elif dmg_type == DamageType.Poison:
            name = "Poisonous Smite"
            condition = f"and forces the target to make a DC {dc} Constitution saving throw or become Poisoned for 1 minute (save ends at end of turn)."
        elif dmg_type == DamageType.Thunder:
            name = "Thundrous Smite"
            dazed = Dazed()
            condition = f"and force the target to make a DC {dc} Constitution saving throw. On a failure, the target is {dazed.caption} until the end of its next turn. {dazed.description_3rd}"
        else:
            raise NotImplementedError(f"{dmg_type} is not supported")

        description = f"Immediately after hitting with an attack, {stats.selfref} deals an additional {dmg} {dmg_type} damage to the target {condition}"

        feature = Feature(
            name=name, action=ActionType.BonusAction, description=description, recharge=5
        )

        return stats, feature


DamagingAura: Power = _DamagingAura()
ElementalAffinity: Power = _ElementalAffinity()
ElementalBurst: Power = _ElementalBurst()
ElementalMagic: Power = _ElementalMagic()
ElementalShroud: Power = _ElementalShroud()
ElementalSmite: Power = _ElementalSmite()


ElementalPowers: List[Power] = [
    DamagingAura,
    ElementalAffinity,
    ElementalBurst,
    ElementalMagic,
    ElementalShroud,
    ElementalSmite,
]

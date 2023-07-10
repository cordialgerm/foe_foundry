from math import ceil
from typing import List, Tuple

from foe_foundry.features import Feature
from foe_foundry.statblocks import BaseStatblock

from ..attributes import Skills, Stats
from ..creature_types import CreatureType
from ..damage import AttackType, DamageType
from ..features import ActionType, Feature
from ..role_types import MonsterRole
from ..size import Size
from ..statblocks import BaseStatblock
from .power import Power
from .rarity import PowerRarity
from .scores import (
    EXTRA_HIGH_AFFINITY,
    HIGH_AFFINITY,
    LOW_AFFINITY,
    MODERATE_AFFINITY,
    NO_AFFINITY,
)


class _DelightsInSuffering(Power):
    """When attacking a target whose current hit points are below half their hit point maximum,
    this creature has advantage on attack rolls and deals an extra CR damage when they hit."""

    def __init__(self):
        super().__init__(name="Delights in Suffering", rarity=PowerRarity.Uncommon)

    def score(self, candidate: BaseStatblock) -> float:
        # this power makes a lot of sense for cruel enemies
        # cruel factors: Fiend, Monstrosity, Intimidation proficiency, Intimidation expertise, high charisma, Ambusher, Bruiser, Leader
        score = LOW_AFFINITY
        if candidate.creature_type in {CreatureType.Fiend, CreatureType.Monstrosity}:
            score += HIGH_AFFINITY
        if Skills.Intimidation in candidate.attributes.proficient_skills:
            score += HIGH_AFFINITY
        if Skills.Intimidation in candidate.attributes.expertise_skills:
            score += EXTRA_HIGH_AFFINITY
        if candidate.attributes.CHA >= 15:
            score += MODERATE_AFFINITY
        if candidate.role in {MonsterRole.Ambusher, MonsterRole.Bruiser, MonsterRole.Leader}:
            score += MODERATE_AFFINITY
        return score

    def apply(self, stats: BaseStatblock) -> Tuple[BaseStatblock, Feature]:
        # grant intimidation proficiency or expertise
        stats = stats.copy(
            attributes=stats.attributes.grant_proficiency_or_expertise(Skills.Intimidation)
        )

        # use secondary damage type, if there is one
        # if there isn't, set it to poison
        if stats.secondary_damage_type is None:
            stats = stats.copy(secondary_damage_type=DamageType.Poison)

        damage_type = stats.secondary_damage_type
        dmg = int(ceil(stats.cr))
        feature = Feature(
            name="Delights in Suffering",
            description=f"When attacking a target whose current hit points are below half their hit point maximum, this creature has advantage on attack rolls and deals an extra {dmg} {damage_type} damage when they hit.",
            action=ActionType.Feature,
        )
        return stats, feature


class _Lethal(Power):
    """This creature has a +CR bonus to damage rolls, and scores a critical hit on an unmodified attack roll of 18-20."""

    def __init__(self):
        super().__init__(name="Lethal", rarity=PowerRarity.Uncommon)

    def score(self, candidate: BaseStatblock) -> float:
        # this role makes sense for lots of monsters, but Ambushers and Artillery should be a bit more likely to have this
        score = MODERATE_AFFINITY
        if candidate.role in {MonsterRole.Ambusher, MonsterRole.Artillery}:
            score += MODERATE_AFFINITY
        if candidate.secondary_damage_type == DamageType.Poison:
            score += MODERATE_AFFINITY
        return score

    def apply(self, stats: BaseStatblock) -> Tuple[BaseStatblock, Feature]:
        if stats.secondary_damage_type is None:
            stats = stats.copy(secondary_damage_type=DamageType.Poison)
        dmg = int(ceil(stats.cr))
        dmg_type = stats.secondary_damage_type
        feature = Feature(
            name="Lethal",
            description=f"This creature deals an additional {dmg} {dmg_type} on attacks and scores a critical hit on an unmodified attack roll of 18-20",
            action=ActionType.Feature,
        )
        return stats, feature


class _MarkTheTarget(Power):
    """When this creature hits a target with a ranged attack, allies of this creature who can see the target
    have advantage on attack rolls against the target until the start of this creature's next turn.
    """

    def __init__(self):
        super().__init__(name="Mark the Target", rarity=PowerRarity.Uncommon)

    def score(self, candidate: BaseStatblock) -> float:
        # this power makes a lot of sense for leaders, artillery, controllers, high intelligence foes, and ranged foes
        score = LOW_AFFINITY
        if candidate.attributes.INT >= 14:
            score += MODERATE_AFFINITY
        if candidate.attack_type in {AttackType.RangedSpell, AttackType.RangedWeapon}:
            score += MODERATE_AFFINITY
        if candidate.role in {MonsterRole.Artillery, MonsterRole.Controller}:
            score += MODERATE_AFFINITY
        if candidate.role in {MonsterRole.Leader}:
            score += HIGH_AFFINITY
        return score

    def apply(self, stats: BaseStatblock) -> Tuple[BaseStatblock, Feature]:
        feature = Feature(
            name="Mark the Target",
            description=f"Immediately after hitting a target, this creature can mark the target. All allies of this creature who can see the target have advantage on attack rolls against the target until the start of this creature's next turn.",
            uses=3,
            action=ActionType.BonusAction,
        )
        return stats, feature


class _ParryAndRiposte(Power):
    """This creature adds +3 to their Armor Class against one melee attack that would hit them.
    If the attack misses, this creature can immediately make a weapon attack against the creature making the parried attack.
    """

    def __init__(self):
        super().__init__(name="Parry and Riposte", rarity=PowerRarity.Uncommon)

    def score(self, candidate: BaseStatblock) -> float:
        # this monster requires a melee weapon
        # it makes a ton of sense for defenders and leaders
        # clever and dextrous foes get a boost as well
        if candidate.attack_type != AttackType.MeleeWeapon:
            return NO_AFFINITY

        score = MODERATE_AFFINITY
        if candidate.role in {MonsterRole.Defender, MonsterRole.Leader}:
            score += HIGH_AFFINITY
        if candidate.attributes.INT >= 14:
            score += MODERATE_AFFINITY
        if candidate.attributes.WIS >= 14:
            score += MODERATE_AFFINITY
        if candidate.attributes.DEX >= 14:
            score += MODERATE_AFFINITY

        return score

    def apply(self, stats: BaseStatblock) -> Tuple[BaseStatblock, Feature]:
        feature = Feature(
            name="Parry and Riposte",
            description="This creature adds +3 to their Armor Class against one melee attack that would hit them.\
                         If the attack misses, this creature can immediately make a weapon attack against the creature making the parried attack.",
            action=ActionType.Reaction,
            recharge=6,
        )
        return stats, feature


class _QuickRecovery(Power):
    """Quick Recovery (Trait). At the start of this creature's turn, they can attempt a saving throw
    against any effect on them that can be ended by a successful saving throw."""

    def __init__(self):
        super().__init__(name="Quick Recovery", rarity=PowerRarity.Uncommon)

    def score(self, candidate: BaseStatblock) -> float:
        # this power makes a lot of sense for high CR creatures, creatures with high CON (resilient), or high CHA (luck)
        score = LOW_AFFINITY
        if candidate.cr >= 8:
            score += MODERATE_AFFINITY
        if candidate.cr >= 12:
            score += MODERATE_AFFINITY
        if candidate.attributes.CON >= 16:
            score += MODERATE_AFFINITY
        if candidate.attributes.CHA >= 16:
            score += MODERATE_AFFINITY
        if candidate.role == MonsterRole.Leader:
            score += MODERATE_AFFINITY
        return score

    def apply(self, stats: BaseStatblock) -> Tuple[BaseStatblock, Feature]:
        # add CON save proficiency
        new_attrs = stats.attributes.grant_save_proficiency(Stats.CON)
        stats = stats.copy(attributes=new_attrs)

        feature = Feature(
            name="Quick Recovery",
            description="At the start of this creature's turn, they can attempt a saving throw \
                         against any effect on them that can be ended by a successful saving throw",
            action=ActionType.Feature,
        )
        return stats, feature


class _Reposition(Power):
    """Each ally within 60 feet of this creature who can see and hear them
    can immediately move their speed without provoking opportunity attacks."""

    def __init__(self):
        super().__init__(name="Reposition", rarity=PowerRarity.Uncommon)

    def score(self, candidate: BaseStatblock) -> float:
        # this trait makes a lot of sense for leaders and high-int enemies

        if candidate.role == MonsterRole.Leader or candidate.attributes.INT >= 16:
            return EXTRA_HIGH_AFFINITY
        else:
            return NO_AFFINITY

    def apply(self, stats: BaseStatblock) -> Tuple[BaseStatblock, Feature]:
        feature = Feature(
            name="Reposition",
            description="Each ally within 60 ft that can see and hear this creature \
                can immediately move its speed without provoking opportunity attacks",
            action=ActionType.BonusAction,
            uses=1,
        )
        return stats, feature


class _Telekinetic(Power):
    """This creature chooses one creature they can see within 100 feet of them
    weighing less than 400 pounds. The target must succeed on a Strength saving throw
    (DC = 11 + 1/2 CR) or be pulled up to 80 feet directly toward this creature."""

    def __init__(self):
        super().__init__(name="Telekinetic", rarity=PowerRarity.Uncommon)

    def score(self, candidate: BaseStatblock) -> float:
        # this is great for aberrations, psychic focused creatures, and controllers
        score = LOW_AFFINITY
        if candidate.creature_type == CreatureType.Aberration:
            score += MODERATE_AFFINITY
        if candidate.secondary_damage_type == DamageType.Psychic:
            score += MODERATE_AFFINITY
        if candidate.role == MonsterRole.Controller:
            score += HIGH_AFFINITY
        return score

    def apply(self, stats: BaseStatblock) -> Tuple[BaseStatblock, Feature]:
        if stats.secondary_damage_type is None:
            stats = stats.copy(secondary_damage_type=DamageType.Psychic)

        dc = int(ceil(11 + stats.cr / 2.0))

        feature = Feature(
            name="Telekinetic Grasp",
            description=f"This creature chooses one creature they can see within 100 feet weighting less than 400 pounds. \
                The target must succeed on a DC {dc} Strength saving throw or be pulled up to 80 feet directly toward this creature",
            action=ActionType.BonusAction,
        )
        return stats, feature


class _Vanish(Power):
    """This creature can use the Disengage action, then can hide if they have cover"""

    def __init__(self):
        super().__init__(name="Vanish", rarity=PowerRarity.Uncommon)

    def score(self, candidate: BaseStatblock) -> float:
        # this is amazing for ambushers and stealth / DEX fighters
        score = LOW_AFFINITY
        if candidate.primary_attribute == Stats.DEX:
            score += LOW_AFFINITY
        if Skills.Stealth in candidate.attributes.proficient_skills:
            score += MODERATE_AFFINITY
        if Skills.Stealth in candidate.attributes.expertise_skills:
            score += HIGH_AFFINITY
        if candidate.role == MonsterRole.Ambusher:
            score += HIGH_AFFINITY
        return score

    def apply(self, stats: BaseStatblock) -> Tuple[BaseStatblock, Feature]:
        new_attrs = stats.attributes.grant_proficiency_or_expertise(Skills.Stealth)
        stats = stats.copy(attributes=new_attrs)

        feature = Feature(
            name="Vanish",
            description="This creature can use the Disengage action, then can hide if they have cover.",
            action=ActionType.BonusAction,
        )
        return stats, feature


DelightsInSuffering: Power = _DelightsInSuffering()
Lethal: Power = _Lethal()
MarkTheTarget: Power = _MarkTheTarget()
ParryAndRiposte: Power = _ParryAndRiposte()
QuickRecovery: Power = _QuickRecovery()
Reposition: Power = _Reposition()
Telekinetic: Power = _Telekinetic()
Vanish: Power = _Vanish()

UncommonPowers: List[Power] = [
    DelightsInSuffering,
    Lethal,
    MarkTheTarget,
    ParryAndRiposte,
    QuickRecovery,
    Reposition,
    Telekinetic,
    Vanish,
]

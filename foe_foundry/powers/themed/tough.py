from math import ceil
from typing import List, Tuple

from num2words import num2words
from numpy.random import Generator

from foe_foundry.features import Feature
from foe_foundry.powers.power_type import PowerType
from foe_foundry.statblocks import BaseStatblock

from ...attributes import Skills, Stats
from ...creature_types import CreatureType
from ...damage import AttackType, DamageType
from ...features import ActionType, Feature
from ...role_types import MonsterRole
from ...size import Size
from ...statblocks import BaseStatblock
from ..power import Power, PowerType
from ..scores import (
    EXTRA_HIGH_AFFINITY,
    HIGH_AFFINITY,
    LOW_AFFINITY,
    MODERATE_AFFINITY,
    NO_AFFINITY,
)


def _score_has_magic_protection(candidate: BaseStatblock) -> float:
    # this is common amongst fiends, celestials, and fey and high-CR creatures
    score = 0
    if candidate.creature_type in {
        CreatureType.Fey,
        CreatureType.Fiend,
        CreatureType.Celestial,
    }:
        score += MODERATE_AFFINITY
    if candidate.role in {MonsterRole.Defender, MonsterRole.Leader}:
        score += MODERATE_AFFINITY
    if candidate.cr >= 7:
        score += MODERATE_AFFINITY
    return score


class _NotDeadYet(Power):
    """When this creature is reduced to 0 hit points, they drop prone and are indistinguishable from a dead creature.
    At the start of their next turn, this creature stands up without using any movement and has 2x CR hit points.
    They can then take their turn normally."""

    def __init__(self):
        super().__init__(name="Not Dead Yet", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        # this power makes a lot of sense for undead, oozes, beasts, and monstrosities
        score = 0
        if candidate.creature_type in {
            CreatureType.Ooze,
            CreatureType.Undead,
            CreatureType.Beast,
            CreatureType.Monstrosity,
        }:
            score += HIGH_AFFINITY
        if Skills.Deception in candidate.attributes.proficient_skills:
            score += MODERATE_AFFINITY
        if Skills.Deception in candidate.attributes.proficient_skills:
            score += HIGH_AFFINITY
        return score if score > 0 else NO_AFFINITY

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        new_attrs = stats.attributes.grant_proficiency_or_expertise(Skills.Deception)
        stats = stats.copy(attributes=new_attrs)

        hp = int(ceil(2.0 * stats.cr))

        feature = Feature(
            name="Not Dead Yet",
            description=f"When {stats.selfref} is reduced to 0 hit points, it drops prone and is indistinguishable from a dead creature. \
                        At the start of their next turn, {stats.selfref} stands up without using any movement and has {hp} hit points. It can take its turn normally",
            action=ActionType.Reaction,
            uses=1,
        )
        return stats, feature


class _GoesDownFighting(Power):
    """When this creature is reduced to 0 hit points, they can immediately make one melee or ranged weapon attack before they fall unconscious."""

    def __init__(self):
        super().__init__(name="Goes Down Fighting", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        # this role makes sense for lots of monsters, but Defenders and Bruisers should be a bit more likely to have this
        score = MODERATE_AFFINITY
        if candidate.role in {MonsterRole.Defender, MonsterRole.Bruiser}:
            score += MODERATE_AFFINITY
        return score

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        feature = Feature(
            name="Goes Down Fighting",
            description=f"When {stats.selfref} is reduced to 0 hit points, they can immediately make one attack before they fall unconscious",
            action=ActionType.Reaction,
        )
        return stats, feature


class _RefuseToSurrender(Power):
    """When this creature’s current hit points are below half their hit point maximum,
    the creature deals CR extra damage with each of their attacks."""

    def __init__(self):
        super().__init__(name="Refuse to Surrender", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        # the creature has to be somewhat aware to fight harder when it's hurt
        if candidate.attributes.INT <= 3 and candidate.attributes.WIS <= 3:
            return NO_AFFINITY

        # this power makes a lot of sense for larger creatures, creatures with more HP, higher CR creatures, and Bruisers
        score = 0
        if candidate.size in {Size.Large, Size.Huge, Size.Gargantuan}:
            score += LOW_AFFINITY
        if candidate.attributes.CON >= 14:
            score += LOW_AFFINITY
        if candidate.cr >= 4:
            score += LOW_AFFINITY
        if candidate.role in {MonsterRole.Bruiser, MonsterRole.Defender}:
            score += MODERATE_AFFINITY
        return score if score > 0 else NO_AFFINITY

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        threshold = int(ceil(stats.hp.average / 2.0))
        dmg = int(ceil(stats.cr))
        feature = Feature(
            name="Refuse to Surrender",
            description=f"When {stats.selfref}'s current hit points are below {threshold}, the creature deals an extra {dmg} damage with each of its attacks.",
            action=ActionType.Feature,
        )
        return stats, feature


class _AdrenalineRush(Power):
    def __init__(self):
        super().__init__(name="Adrenaline Rush", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        # this is amazing for ambushers, bruisers, and melee fighters
        score = 0
        if candidate.primary_attribute in {Stats.DEX, Stats.STR}:
            score += MODERATE_AFFINITY
        if candidate.role in {MonsterRole.Ambusher, MonsterRole.Bruiser}:
            score += MODERATE_AFFINITY
        if candidate.creature_type == CreatureType.Humanoid:
            score += LOW_AFFINITY
        return score

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        feature = Feature(
            name="Adrenaline Rush",
            uses=1,
            action=ActionType.BonusAction,
            description=f"{stats.selfref.capitalize()} takes another action this round. If it has any recharge abilities, it may roll to refresh these abilities.",
        )

        return stats, feature


class _MagicResistance(Power):
    def __init__(self):
        super().__init__(name="Magic Resistance", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        score = _score_has_magic_protection(candidate)
        return score if score > 0 else NO_AFFINITY

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        feature = Feature(
            name="Magic Resistance",
            action=ActionType.Feature,
            description=f"{stats.selfref.capitalize()} has advantage on saves against spells and other magical effects.",
        )

        return stats, feature


class _LimitedMagicImmunity(Power):
    def __init__(self):
        super().__init__(name="Limited Magic Immunity", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        score = _score_has_magic_protection(candidate)
        return score if score > 0 else NO_AFFINITY

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        level = (
            f"{num2words(int(min(5, ceil(stats.cr / 3))), to='ordinal')} level spell or lower"
        )

        feature = Feature(
            name="Limited Magic Immunity",
            action=ActionType.Reaction,
            description=f"When {stats.selfref} is attacked by a spell, targeted by spell, or forced to make a saving throw by a {level} then {stats.selfref} can force the spell attack to miss or can choose to succeed on the saving throw.",
        )

        return stats, feature


AdrenalineRush: Power = _AdrenalineRush()
GoesDownFighting: Power = _GoesDownFighting()
LimitedMagicImmunity: Power = _LimitedMagicImmunity()
MagicResistance: Power = _MagicResistance()
NotDeadYet: Power = _NotDeadYet()
RefuseToSurrender: Power = _RefuseToSurrender()

ToughPowers: List[Power] = [
    AdrenalineRush,
    GoesDownFighting,
    LimitedMagicImmunity,
    MagicResistance,
    NotDeadYet,
    RefuseToSurrender,
]
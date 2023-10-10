from typing import List, Tuple

from numpy.random import Generator

from foe_foundry.features import Feature
from foe_foundry.statblocks import BaseStatblock

from ...creature_types import CreatureType
from ...features import ActionType, Feature
from ...role_types import MonsterRole
from ...size import Size
from ...skills import Skills, Stats
from ...statblocks import BaseStatblock
from ..power import Power, PowerType
from ..scores import (
    EXTRA_HIGH_AFFINITY,
    HIGH_AFFINITY,
    LOW_AFFINITY,
    MODERATE_AFFINITY,
    NO_AFFINITY,
)


class _Defender(Power):
    """When an ally within 5 feet of this creature is targeted by an attack or spell, this creature can make themself the intended target of the attack."""

    def __init__(self):
        super().__init__(name="Defender", power_type=PowerType.Role)

    def _is_minion(self, candidate: BaseStatblock) -> bool:
        return candidate.cr <= 2 and candidate.role not in {
            MonsterRole.Ambusher,
            MonsterRole.Controller,
            MonsterRole.Leader,
            MonsterRole.Skirmisher,
        }

    def score(self, candidate: BaseStatblock) -> float:
        # this power makes a lot of sense for minions and defensive creatures
        # for now, I will interpret minions as low CR creatures
        score = 0
        if self._is_minion(candidate):
            score += MODERATE_AFFINITY

        if candidate.role == MonsterRole.Defender:
            score += EXTRA_HIGH_AFFINITY

        return score if score > 0 else NO_AFFINITY

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        name = "Cannon Fodder" if self._is_minion(stats) else "Defender"

        feature = Feature(
            name=name,
            description=f"When an ally within 5 feet is targeted by an attack or spell, {stats.selfref} can make themselves the intended target of the attack or spell instead.",
            action=ActionType.Reaction,
        )
        return stats, feature


class _StickWithMe(Power):
    def __init__(self):
        super().__init__(name="Stick with Me!", power_type=PowerType.Role)

    def score(self, candidate: BaseStatblock) -> float:
        if not candidate.attack_type.is_melee():
            return NO_AFFINITY

        score = 0

        if candidate.role == MonsterRole.Defender:
            score += HIGH_AFFINITY

        if candidate.uses_shield:
            score += MODERATE_AFFINITY

        if candidate.attributes.has_proficiency_or_expertise(Skills.Intimidation):
            score += LOW_AFFINITY

        if candidate.creature_type.could_wear_armor:
            score += LOW_AFFINITY

        return score if score > 0 else NO_AFFINITY

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        feature = Feature(
            name="Stick with Me!",
            description=f"On a hit, the target has disadvantage on attack rolls against any other creature until the end of its next turn.",
            action=ActionType.Feature,
            hidden=True,
            modifies_attack=True,
        )
        return stats, feature


class _Blocker(Power):
    def __init__(self):
        super().__init__(name="Blocker", power_type=PowerType.Role)

    def score(self, candidate: BaseStatblock) -> float:
        score = 0

        if candidate.role == MonsterRole.Defender:
            score += MODERATE_AFFINITY

        if candidate.primary_attribute == Stats.STR:
            score += MODERATE_AFFINITY

        if candidate.attributes.has_proficiency_or_expertise(Skills.Athletics):
            score += MODERATE_AFFINITY

        if candidate.size >= Size.Large:
            score += LOW_AFFINITY

        return score if score > 0 else NO_AFFINITY

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        new_attrs = stats.attributes.grant_proficiency_or_expertise(Skills.Athletics)
        stats = stats.copy(attributes=new_attrs)

        feature = Feature(
            name="Blocker",
            description=f"Any creature starting their turn next to {stats.selfref} has their speed reduced by half until the end of their turn.",
            action=ActionType.Feature,
        )

        return stats, feature


class _SpellReflection(Power):
    def __init__(self):
        super().__init__(name="Blocker", power_type=PowerType.Role)

    def score(self, candidate: BaseStatblock) -> float:
        score = 0
        if candidate.role == MonsterRole.Default:
            score += HIGH_AFFINITY

        if candidate.creature_type in {
            CreatureType.Aberration,
            CreatureType.Dragon,
            CreatureType.Fiend,
            CreatureType.Monstrosity,
        }:
            score += MODERATE_AFFINITY

        if candidate.attack_type.is_spell():
            score += MODERATE_AFFINITY

        return score if score > 0 else NO_AFFINITY

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        feature = Feature(
            name="Spell Reflection",
            action=ActionType.Reaction,
            description=f"If {stats.selfref} succeeds on a saving throw against a spell or if a spell attack misses it, then {stats.selfref} can choose another creature (including the spellcaster) it can see within 120 feet of it. \
                The spell or attack targets the chosen creature instead.",
        )

        return stats, feature


Blocker: Power = _Blocker()
Defender: Power = _Defender()
StickWithMe: Power = _StickWithMe()
SpellReflection: Power = _SpellReflection()


DefenderPowers: List[Power] = [Blocker, Defender, StickWithMe, SpellReflection]

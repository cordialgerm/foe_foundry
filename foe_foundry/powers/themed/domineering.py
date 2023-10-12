from math import ceil
from typing import List, Tuple

from num2words import num2words
from numpy.random import Generator

from foe_foundry.features import Feature
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


def _score_is_domineering(candidate: BaseStatblock, min_cr: int = 3) -> float:
    if candidate.attributes.CHA <= 14:
        return NO_AFFINITY

    if candidate.cr < 5:
        return NO_AFFINITY

    creature_types = {
        CreatureType.Fiend: HIGH_AFFINITY,
        CreatureType.Fey: MODERATE_AFFINITY,
        CreatureType.Dragon: HIGH_AFFINITY,
        CreatureType.Celestial: MODERATE_AFFINITY,
        CreatureType.Undead: MODERATE_AFFINITY,
    }

    roles = {MonsterRole.Leader: HIGH_AFFINITY, MonsterRole.Controller: MODERATE_AFFINITY}

    score = 0
    score += creature_types.get(candidate.creature_type, 0)
    score += roles.get(candidate.role, 0)
    return score if score > 0 else NO_AFFINITY


def _ensure_domineering(stats: BaseStatblock) -> BaseStatblock:
    new_attributes = stats.attributes.boost(Stats.CHA, 4).grant_proficiency_or_expertise(
        Skills.Persuasion
    )
    stats = stats.copy(attributes=new_attributes)
    return stats


class _CommandingPresence(Power):
    def __init__(self):
        super().__init__(name="Commanding Presence", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return _score_is_domineering(candidate)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        stats = _ensure_domineering(stats)

        dc = stats.difficulty_class

        targets = num2words(int(ceil(max(5, stats.cr / 3))))

        feature = Feature(
            name="Commanding Presence",
            action=ActionType.BonusAction,
            description=f"{stats.selfref.capitalize()} chooses up to {targets} creatures it can see within 60 feet and attempts to magically compell them \
                 to grovel. The creatures must make a DC {dc} Wisdom save or be affected as by the *Command* spell. A creature that saves is immune to this effect for 24 hours.",
        )
        return stats, feature


class _Charm(Power):
    def __init__(self):
        super().__init__(name="Commanding Presence", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return _score_is_domineering(candidate, min_cr=7)

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, Feature | List[Feature]]:
        stats = _ensure_domineering(stats)

        if stats.creature_type == CreatureType.Fey:
            name = "Fey Charm"
        elif stats.creature_type == CreatureType.Dragon:
            name = "Draconic Charm"
        elif stats.creature_type == CreatureType.Celestial:
            name = "Celestial Charm"
        elif stats.creature_type == CreatureType.Fiend:
            name = "Fiendish Charm"
        else:
            name = "Charm"

        dc = stats.difficulty_class_easy

        feature = Feature(
            name=name,
            action=ActionType.Action,
            replaces_multiattack=2,
            description=f"{stats.selfref.capitalize()} targets one humanoid it can see within 30 feet of it. If the target can see {stats.selfref} \
                then it must succeed on a DC {dc} Wisdom save against this magic or be **Charmed** by {stats.selfref}. \
                While charmed in this way, the target treats {stats.selfref} as a trusted friend to be heeded and protected. \
                It takes {stats.selfref}'s requests or actions in the most favorable way it can.  \
                Each time the target takes damage, it may repeat the save to end the condition. \
                Otherwise, the effect lasts for 24 hours or until {stats.selfref} dies or is on anther plane of existance. \
                A creature that saves is immune to this effect for 24 hours.",
        )

        return stats, feature


Charm: Power = _Charm()
CommandingPresence: Power = _CommandingPresence()

DomineeringPowers: List[Power] = [Charm, CommandingPresence]

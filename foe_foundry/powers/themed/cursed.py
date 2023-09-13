from math import ceil, floor
from typing import List, Tuple

import numpy as np
from numpy.random import Generator

from foe_foundry.features import Feature
from foe_foundry.powers.power_type import PowerType
from foe_foundry.statblocks import BaseStatblock

from ...ac import ArmorClass
from ...attributes import Skills, Stats
from ...creature_types import CreatureType
from ...damage import AttackType, DamageType
from ...features import ActionType, Feature
from ...role_types import MonsterRole
from ...size import Size
from ...statblocks import BaseStatblock, MonsterDials
from ..power import Power, PowerType
from ..scores import (
    EXTRA_HIGH_AFFINITY,
    HIGH_AFFINITY,
    LOW_AFFINITY,
    MODERATE_AFFINITY,
    NO_AFFINITY,
)


def _score_cursed(candidate: BaseStatblock) -> float:
    score = 0

    creature_types = {
        CreatureType.Fey: HIGH_AFFINITY,
        CreatureType.Fiend: HIGH_AFFINITY,
        CreatureType.Undead: HIGH_AFFINITY,
    }
    score += creature_types.get(candidate.creature_type, 0)

    if candidate.secondary_damage_type == DamageType.Necrotic:
        score += HIGH_AFFINITY

    return score if score > 0 else NO_AFFINITY


def _as_cursed(stats: BaseStatblock) -> BaseStatblock:
    if stats.secondary_damage_type != DamageType.Necrotic:
        stats = stats.copy(secondary_damage_type=DamageType.Necrotic)

    return stats


class _DevilsSight(Power):
    def __init__(self):
        super().__init__(name="Devil's Sight", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        score = 0

        if candidate.creature_type == CreatureType.Fiend:
            score += EXTRA_HIGH_AFFINITY

        return score if score > 0 else NO_AFFINITY

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, List[Feature]]:
        stats = stats.copy(creature_type=CreatureType.Fiend)

        level = 2 if stats.cr <= 5 else 4

        devils_sight = Feature(
            name="Devil's Sight",
            action=ActionType.Feature,
            description=f"Magical darkness doesn't impede {stats.selfref}'s darkvision, and it can see through Hellish Darkness.",
        )

        darkness = Feature(
            name="Hellish Darkness",
            action=ActionType.BonusAction,
            recharge=5,
            description=f"{stats.selfref.capitalize()} causes shadowy black flames to fill a 15-foot radius sphere with obscuring darkness centered at a point within 60 feet that {stats.selfref} can see. \
                The darkness spreads around corners. Creatures without Devil's Sight can't see through this darkness and nonmagical light can't illuminate it. \
                If any of this spell's area overlaps with an area of light created by a spell of level {level} or lower, the spell that created the light is dispelled. \
                Creatures of {stats.selfref}'s choice lose any resistance to fire damage while in the darkness, and immunity to fire damage is instead treated as resistance to fire damage.",
        )

        return stats, [devils_sight, darkness]


class _AuraOfDespair(Power):
    def __init__(self):
        super().__init__(name="Aura of Despair", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return _score_cursed(candidate)

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, Feature | List[Feature]]:
        stats = _as_cursed(stats)

        weight_of_sorrow = Feature(
            name="Weight of Sorrow",
            action=ActionType.Feature,
            description=f"Any creature othern than {stats.selfref} that starts its turn within 5 feet of {stats.selfref} has its speed reduced by 20 feet until the start of that creature's next turn.",
        )

        dc = stats.difficulty_class

        dreadful_scream = Feature(
            name="Dreadful Scream",
            action=ActionType.Action,
            recharge=5,
            replaces_multiattack=1,
            description=f"{stats.selfref.capitalize()} unleashes a dreadful scream laced with sorrow and despair. \
                Each creature within 30 feet that can hear {stats.selfref} must make a DC {dc} Wisdom saving throw or be frightened of {stats.selfref} for 1 minute (save ends at end of turn). \
                While frightened in this way, the creature loses any resistance or immunity to psychic and necrotic damage.",
        )

        return stats, [weight_of_sorrow, dreadful_scream]


class _HorriblyDisfigured(Power):
    def __init__(self):
        return super().__init__(name="Horribly Disfigured", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return _score_cursed(candidate)

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, Feature | List[Feature]]:
        stats = _as_cursed(stats)
        dc = stats.difficulty_class_easy
        dmg = int(floor(5 + 2 * stats.cr))

        feature = Feature(
            name="Disfiguring Curse",
            action=ActionType.Action,
            uses=1,
            replaces_multiattack=1,
            description=f"{stats.selfref.capitalize()} attempts to magically spread its curse to a target that it can see within 60 feet. \
                The target must make DC {dc} Charisma save. On a failure, the target takes {dmg} psychic damage and is cursed with magical deformities. \
                While deformed, the creature's speed is halved and it has disadvantage on ability checks, saving throws, and attacks. \
                The cursed creature can repeat the saving throw whenever it finishes a long rest, ending the effect on a success.",
        )

        return stats, feature


class _CursedWound(Power):
    def __init__(self):
        return super().__init__(name="Cursed Wound", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return _score_cursed(candidate)

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, Feature | List[Feature]]:
        stats = _as_cursed(stats)

        dc = stats.difficulty_class

        feature = Feature(
            name="Cursed Wounds",
            action=ActionType.BonusAction,
            description=f"Immediately after hitting with an attack, {stats.selfref} converts all of that attack's damage to necrotic damage and forces the target to make a DC {dc} Charisma save. \
                On a failure, the target is cursed and its maximum hit points are reduced by the necrotic damage taken. \
                The target dies and reanimates as a Zombie under the control of {stats.selfref} if this damage leaves it with 0 hit points.",
        )

        return stats, feature


DevilsSight: Power = _DevilsSight()
CursedWound: Power = _CursedWound()
HorriblyDisfigured: Power = _HorriblyDisfigured()
AuraOfDespair: Power = _AuraOfDespair()

CursedPowers: List[Power] = [DevilsSight, CursedWound, HorriblyDisfigured, AuraOfDespair]

from math import floor
from typing import List, Tuple

import numpy as np
from numpy.random import Generator

from foe_foundry.features import Feature
from foe_foundry.powers.power_type import PowerType
from foe_foundry.statblocks import BaseStatblock

from ...attributes import Skills, Stats
from ...creature_types import CreatureType
from ...damage import AttackType, DamageType
from ...features import ActionType, Feature
from ...role_types import MonsterRole
from ...statblocks import BaseStatblock
from ..power import Power, PowerType
from ..scores import (
    EXTRA_HIGH_AFFINITY,
    HIGH_AFFINITY,
    LOW_AFFINITY,
    MODERATE_AFFINITY,
    NO_AFFINITY,
)


def _score_is_tricky_creature(candidate: BaseStatblock) -> float:
    score = 0

    creature_types = {
        CreatureType.Fey: HIGH_AFFINITY,
        CreatureType.Fiend: MODERATE_AFFINITY,
        CreatureType.Aberration: MODERATE_AFFINITY,
        CreatureType.Ooze: MODERATE_AFFINITY,
        CreatureType.Humanoid: MODERATE_AFFINITY,
    }
    score += creature_types.get(candidate.creature_type, 0)

    if score == 0:
        return 0

    roles = {MonsterRole.Ambusher: LOW_AFFINITY, MonsterRole.Controller: LOW_AFFINITY}
    score += roles.get(candidate.role, 0)

    if candidate.secondary_damage_type == DamageType.Psychic:
        score += LOW_AFFINITY

    if candidate.attributes.has_proficiency_or_expertise(Skills.Deception):
        score += MODERATE_AFFINITY

    return score


def _ensure_tricky_stats(stats: BaseStatblock) -> BaseStatblock:
    # this creature should be tricky
    new_attrs = stats.attributes.grant_proficiency_or_expertise(Skills.Deception).boost(
        Stats.CHA, 2
    )

    changes: dict = dict(attributes=new_attrs)

    # if this is a humanoid, it should be an illusionist spellcaster
    if stats.creature_type == CreatureType.Humanoid:
        changes.update(
            attack_type=AttackType.RangedSpell, secondary_damage_type=DamageType.Psychic
        )

    return stats.copy(**changes)


class _NimbleReaction(Power):
    def __init__(self):
        super().__init__(name="Nimble Reaction", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        score = 0

        if candidate.primary_attribute == Stats.DEX:
            score += LOW_AFFINITY

        if candidate.attributes.has_proficiency_or_expertise(Skills.Acrobatics):
            score += HIGH_AFFINITY

        if candidate.speed.fastest_speed >= 40:
            score += MODERATE_AFFINITY

        return score if score > 0 else NO_AFFINITY

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        new_attrs = stats.attributes.grant_proficiency_or_expertise(Skills.Acrobatics)
        stats = stats.copy(attributes=new_attrs)

        feature = Feature(
            name="Nimble Reaction",
            action=ActionType.Reaction,
            description=f"When {stats.selfref} is the only target of a melee attack, they can move up to their speed without provoking opportunity attacks.\
                If this movement leaves {stats.selfref} outside the attacking creature's reach, then the attack misses.",
            recharge=4,
        )

        return stats, feature


class _Impersonation(Power):
    def __init__(self):
        super().__init__(name="Impersonation", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        score = _score_is_tricky_creature(candidate)
        return score if score > 0 else NO_AFFINITY

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        stats = _ensure_tricky_stats(stats)

        dc = 8 + stats.attributes.stat_mod(Stats.CHA) + stats.attributes.proficiency

        feature = Feature(
            name="Impersonation",
            action=ActionType.BonusAction,
            recharge=6,
            description=f"Until the start of their next turn, {stats.selfref} changes their appearance to look exactly like another creature who is within 5 feet of them \
                    and is no more than one size smaller or larger. Other creatures must make a DC {dc} Perception check each time they make an attack against {stats.selfref} or the impersonated creature. \
                    On a failure, the attack is made against the wrong target, without the attacker knowing.",
        )

        return stats, feature


class _Projection(Power):
    def __init__(self):
        super().__init__(name="Projection", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        score = _score_is_tricky_creature(candidate)
        return score if score > 0 else NO_AFFINITY

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        stats = _ensure_tricky_stats(stats)

        dc = stats.attributes.passive_skill(Skills.Deception)

        feature = Feature(
            name="Projection",
            action=ActionType.Reaction,
            uses=1,
            description=f"When {stats.selfref} is the sole target of an attack or spell, {stats.selfref} may use their reaction to turn invisible and teleport up to 30 ft to an unoccupied location they can see. \
                The invisibility lasts for up to 1 minute or until {stats.selfref} makes an attack or casts a spell. \
                Simultaneously, an illusionary version of {stats.selfref} appears in the previous location and appears to be subjected to the attack or spell. \
                The illusion ends when the invisibility ends and also fails to stand up to physical interaction. A character may also use an action to perform a DC {dc} Investigation check to identify the illusion.",
        )

        return stats, feature


class _EvilDoppelganger(Power):
    def __init__(self):
        super().__init__(name="Evil Doppelganger", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return _score_is_tricky_creature(candidate)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        dc = stats.difficulty_class
        hp = int(floor(max(5, 2 * stats.cr)))

        feature = Feature(
            name="Evil Doppleganger",
            action=ActionType.Action,
            uses=1,
            description=f"{stats.selfref.capitalize()} forces each creature of its choice within 30 feet to make a DC {dc} Charisma saving throw. \
                On a failure, a Shadow Doppleganger copy of that creature materializes in the nearest unoccupied space to that creature and acts in initiative immediately after {stats.selfref}. \
                The Shadow Doppleganger has {hp} hp and has an AC equal to the creature it was copied from and is an Undead. On its turn, the Shadow Doppleganger attempts to move and attack the creature it was copied from. \
                It makes a single attack using {stats.selfref}'s Attack action. It otherwise has the movement, stats, skills, and saves of the creature it was copied from.",
        )

        return stats, feature


class _SpectralDuplicate(Power):
    def __init__(self):
        super().__init__(name="Spectral Duplicate", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return _score_is_tricky_creature(candidate)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        feature = Feature(
            name="Spectral Duplicate",
            action=ActionType.BonusAction,
            uses=1,
            description=f"{stats.selfref.capitalize()} creates a spectral duplicate of itself in an unoccupied space it can see within 60 feet. \
                While the duplicate exists, {stats.selfref} is invisible and unconscious. The duplicate has the same statistics and knowledge as {stats.selfref} \
                and acts immediately in initiative after {stats.selfref}. The duplicate disappears when {stats.selfref} drops to 0 hp.",
        )

        return stats, feature


class _MirrorImage(Power):
    def __init__(self):
        super().__init__(name="Mirror Images", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return _score_is_tricky_creature(candidate)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        ac = 10 + stats.attributes.DEX

        feature = Feature(
            name="Mirror Images",
            action=ActionType.BonusAction,
            uses=1,
            description=f"{stats.selfref.capitalize()} magically creates three illusory duplicates of itself as in the *Mirror Image* spell. The duplicates have AC {ac}",
        )
        return stats, feature


class _Hypnosis(Power):
    def __init__(self):
        super().__init__(name="Hypnotic Pattern", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return _score_is_tricky_creature(candidate)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        dc = stats.difficulty_class_easy

        feature = Feature(
            name="Hypnotic Pattern",
            action=ActionType.Action,
            uses=1,
            replaces_multiattack=2,
            description=f"{stats.selfref.capitalize()} magically creates the effect of the *Hypnotic Pattern* spell, using a DC of {dc}",
        )

        return stats, feature


class _ReverseFortune(Power):
    def __init__(self):
        super().__init__(name="Reverse Fortune", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return _score_is_tricky_creature(candidate)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        feature = Feature(
            name="Reverse Fortune",
            action=ActionType.Reaction,
            recharge=4,
            description=f"When {stats.selfref} is hit by an attack, {stats.selfref} magically reverses the fortune of the attack and forces it to miss. \
                Until the end of its next turn, {stats.selfref} gains advantage on the next attack it makes against the attacker.",
        )

        return stats, feature


EvilDoppleganger: Power = _EvilDoppelganger()
Hypnosis: Power = _Hypnosis()
Impersonation: Power = _Impersonation()
MirrorImage: Power = _MirrorImage()
NimbleReaction: Power = _NimbleReaction()
Projection: Power = _Projection()
ReverseFortune: Power = _ReverseFortune()
SpectralDuplicate: Power = _SpectralDuplicate()

TrickyPowers: List[Power] = [
    EvilDoppleganger,
    Hypnosis,
    Impersonation,
    MirrorImage,
    NimbleReaction,
    Projection,
    ReverseFortune,
    SpectralDuplicate,
]

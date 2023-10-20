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
from ...utils import easy_multiple_of_five
from ..power import HIGH_POWER, Power, PowerBackport, PowerType
from ..scoring import score


def _score_is_tricky_creature(candidate: BaseStatblock) -> float:
    def is_powerfully_magical(c: BaseStatblock) -> bool:
        return c.attributes.spellcasting_mod >= 3 or c.attack_type.is_spell()

    return score(
        candidate=candidate,
        require_types={
            CreatureType.Fey,
            CreatureType.Fiend,
            CreatureType.Aberration,
            CreatureType.Humanoid,
        },
        require_callback=is_powerfully_magical,
        bonus_roles={MonsterRole.Ambusher, MonsterRole.Controller},
        require_stats=[Stats.CHA, Stats.INT],
    )


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


class _Impersonation(PowerBackport):
    def __init__(self):
        super().__init__(name="Impersonation", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return _score_is_tricky_creature(candidate)

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


class _Projection(PowerBackport):
    def __init__(self):
        super().__init__(name="Projection", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return _score_is_tricky_creature(candidate)

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


class _ShadowyDoppelganger(PowerBackport):
    def __init__(self):
        super().__init__(
            name="Shadowy Doppelganger", power_type=PowerType.Theme, power_level=HIGH_POWER
        )

    def score(self, candidate: BaseStatblock) -> float:
        return _score_is_tricky_creature(candidate)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        dc = stats.difficulty_class
        hp = easy_multiple_of_five(1.25 * stats.cr, min_val=5)

        feature = Feature(
            name="Shadowy Doppleganger",
            action=ActionType.Action,
            uses=1,
            description=f"{stats.selfref.capitalize()} forces each non-fey creature of its choice within 30 feet to make a DC {dc} Charisma saving throw. \
                On a failure, a Shadow Doppleganger copy of that creature materializes in the nearest unoccupied space to that creature and acts in initiative immediately after {stats.selfref}. \
                The Shadow Doppleganger has {hp} hp and has an AC equal to the creature it was copied from and is a Fey. On its turn, the Shadow Doppleganger attempts to move and attack the creature it was copied from. \
                It makes a single attack using the stats of {stats.selfref}'s Attack action. It otherwise has the movement, stats, skills, and saves of the creature it was copied from.",
        )

        return stats, feature


class _SpectralDuplicate(PowerBackport):
    def __init__(self):
        super().__init__(
            name="Spectral Duplicate", power_type=PowerType.Theme, power_level=HIGH_POWER
        )

    def score(self, candidate: BaseStatblock) -> float:
        return _score_is_tricky_creature(candidate)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        feature = Feature(
            name="Spectral Duplicate",
            action=ActionType.BonusAction,
            uses=1,
            description=f"{stats.selfref.capitalize()} creates a spectral duplicate of itself in an unoccupied space it can see within 60 feet. \
                While the duplicate exists, {stats.selfref} is **Invisible** and **Unconscious**. The duplicate has the same statistics and knowledge as {stats.selfref} \
                and acts immediately in initiative after {stats.selfref}. The duplicate disappears when {stats.selfref} drops to 0 hp.",
        )

        return stats, feature


class _MirrorImage(PowerBackport):
    def __init__(self):
        super().__init__(name="Mirror Images", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return _score_is_tricky_creature(candidate)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        ac = 10 + stats.attributes.stat_mod(Stats.DEX)

        feature = Feature(
            name="Mirror Images",
            action=ActionType.BonusAction,
            uses=1,
            description=f"{stats.selfref.capitalize()} magically creates three illusory duplicates of itself as in the *Mirror Image* spell. The duplicates have AC {ac}",
        )
        return stats, feature


class _Hypnosis(PowerBackport):
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


class _ReverseFortune(PowerBackport):
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


Hypnosis: Power = _Hypnosis()
Impersonation: Power = _Impersonation()
MirrorImage: Power = _MirrorImage()
Projection: Power = _Projection()
ReverseFortune: Power = _ReverseFortune()
ShadowyDoppelganger: Power = _ShadowyDoppelganger()
SpectralDuplicate: Power = _SpectralDuplicate()

TrickyPowers: List[Power] = [
    Hypnosis,
    Impersonation,
    MirrorImage,
    Projection,
    ReverseFortune,
    ShadowyDoppelganger,
    SpectralDuplicate,
]

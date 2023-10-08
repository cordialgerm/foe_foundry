from math import ceil
from typing import Dict, List, Tuple

import numpy as np
from numpy.random import Generator

from foe_foundry.features import Feature
from foe_foundry.statblocks import BaseStatblock

from ...attack_template import natural as natural_attacks
from ...attributes import Skills, Stats
from ...creature_types import CreatureType
from ...damage import AttackType, Burning, DamageType, Dazed
from ...die import Die, DieFormula
from ...features import ActionType, Feature
from ...role_types import MonsterRole
from ...size import Size
from ...statblocks import BaseStatblock
from ...utils import easy_multiple_of_five
from ..power import Power, PowerType
from ..scores import (
    EXTRA_HIGH_AFFINITY,
    HIGH_AFFINITY,
    LOW_AFFINITY,
    MODERATE_AFFINITY,
    NO_AFFINITY,
)


def _score_is_psychic(
    candidate: BaseStatblock,
    require_aberration: bool = False,
    min_cr: float | None = None,
    attack_modifiers: Dict[str, float] | None = None,
) -> float:
    # this is great for aberrations, psychic focused creatures, and controllers
    score = 0

    if require_aberration and not candidate.creature_type == CreatureType.Aberration:
        return NO_AFFINITY

    if min_cr and candidate.cr < min_cr:
        return NO_AFFINITY

    if candidate.creature_type == CreatureType.Aberration:
        score += HIGH_AFFINITY
    if candidate.secondary_damage_type == DamageType.Psychic:
        score += HIGH_AFFINITY
    if candidate.role == MonsterRole.Controller:
        score += MODERATE_AFFINITY

    default_attack_modifier = attack_modifiers.get("*", 0) if attack_modifiers else 0
    attack_modifier = (
        attack_modifiers.get(candidate.attack.name, default_attack_modifier)
        if attack_modifiers
        else 0
    )

    score += attack_modifier

    return score if score > 0 else NO_AFFINITY


def as_psychic(stats: BaseStatblock) -> BaseStatblock:
    if stats.secondary_damage_type is None:
        stats = stats.copy(secondary_damage_type=DamageType.Psychic)
    return stats


class _Telekinetic(Power):
    """This creature chooses one creature they can see within 100 feet of them
    weighing less than 400 pounds. The target must succeed on a Strength saving throw
    (DC = 11 + 1/2 CR) or be pulled up to 80 feet directly toward this creature."""

    def __init__(self):
        super().__init__(name="Telekinetic", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return _score_is_psychic(candidate)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        stats = as_psychic(stats)

        dc = int(ceil(11 + stats.cr / 2.0))

        feature = Feature(
            name="Telekinetic Grasp",
            description=f"{stats.selfref.capitalize()} chooses one creature they can see within 100 feet weighting less than 400 pounds. \
                The target must succeed on a DC {dc} Strength saving throw or be pulled up to 80 feet directly toward {stats.selfref}",
            action=ActionType.BonusAction,
        )
        return stats, feature


class _PsychicInfestation(Power):
    def __init__(self):
        super().__init__(name="Psychic Infestation", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return _score_is_psychic(candidate)

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, Feature | List[Feature] | None]:
        stats = as_psychic(stats)

        distance = easy_multiple_of_five(30 + 5 * stats.cr, min_val=30, max_val=90)
        dc = stats.difficulty_class
        dmg = DieFormula.target_value(
            target=1.5 * stats.attack.average_damage, force_die=Die.d6
        )
        burning = Burning(
            damage=DieFormula.from_dice(d6=dmg.n_die // 2), damage_type=DamageType.Psychic
        )

        feature = Feature(
            name="Psychic Infestation",
            action=ActionType.Action,
            replaces_multiattack=2,
            recharge=5,
            description=f"{stats.selfref.capitalize()} attempts to infect the mind of a creature it can see within {distance} feet. \
                The creature must make a DC {dc} Intelligence save. On a failure, it takes {dmg.description} psychic damage and is {burning.caption}. \
                On a success, it takes half damage instead. {burning.description_3rd}",
        )

        return stats, feature


class _DissonantWhispers(Power):
    def __init__(self):
        super().__init__(name="Dissonant Whispers", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return _score_is_psychic(candidate)

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, Feature | List[Feature] | None]:
        stats = as_psychic(stats)

        distance = easy_multiple_of_five(30 + 5 * stats.cr, min_val=30, max_val=90)
        dc = stats.difficulty_class
        dmg = DieFormula.target_value(1.5 * stats.attack.average_damage, force_die=Die.d6)

        feature = Feature(
            name="Dissonant Whispers",
            action=ActionType.Action,
            replaces_multiattack=2,
            description=f"{stats.selfref.capitalize()} whispers a discordant melody into the mind of a creature within {distance} ft. \
                The target must make a DC {dc} Wisdom save. On a failure, it takes {dmg.description} psychic damage and must immediately use its reaction, \
                if available, to move as far away as its speed allows from {stats.selfref}. The creature doesn't move into obviously dangerous ground. \
                On a successful save, the target takes half damage instead.",
        )

        return stats, feature


class _MindBlast(Power):
    def __init__(self):
        super().__init__(name="Mind Blast", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return _score_is_psychic(candidate, min_cr=5)

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, Feature | List[Feature] | None]:
        stats = as_psychic(stats)
        multiplier = 2.5 if stats.multiattack >= 2 else 1.5
        dmg = DieFormula.target_value(
            target=multiplier * stats.attack.average_damage, force_die=Die.d6
        )
        dc = stats.difficulty_class

        if stats.cr <= 3:
            distance = 15
        elif stats.cr <= 5:
            distance = 30
        else:
            distance = 60

        feature = Feature(
            name="Mind Blast",
            action=ActionType.Action,
            recharge=6,
            replaces_multiattack=3,
            description=f"{stats.selfref.capitalize()} magically emits psychic energy in a {distance} ft cone. \
                Each creature in that area must succeed on a DC {dc} Intelligence saving throw. On a failure, a creature \
                takes {dmg.description} psychic damage and is **Stunned** for 1 minute (save ends at end of turn). On a failure, \
                a creature takes half damage instead.",
        )

        return stats, feature


class _PsychicMirror(Power):
    def __init__(self):
        super().__init__(name="Psychic Mirror", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return _score_is_psychic(candidate)

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, Feature | List[Feature] | None]:
        stats = as_psychic(stats)

        feature = Feature(
            name="Psychic Mirror",
            action=ActionType.Reaction,
            description=f"Whenever {stats.selfref} takes psychic damage, each other creature within 10 feet of {stats.selfref} takes that damage instead.",
        )

        return stats, feature


class _ExtractBrain(Power):
    def __init__(self):
        super().__init__(name="Extract Brain", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return _score_is_psychic(
            candidate,
            require_aberration=True,
            min_cr=7,
            attack_modifiers={
                "*": NO_AFFINITY,
                natural_attacks.Tentacle.attack_name: HIGH_AFFINITY,
            },
        )

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, Feature | List[Feature] | None]:
        stats = as_psychic(stats)

        dc = stats.difficulty_class_easy
        dazed = Dazed()

        stunning_tentacles = Feature(
            name="Stunning Tentancles",
            action=ActionType.Feature,
            hidden=True,
            modifies_attack=True,
            description=f"On a hit, the target is **Grappled** (escape DC {dc}) and must succeed \
                on a DC {dc} Intelligence save or be {dazed.caption} while grappled in this way. {dazed.description_3rd}",
        )

        extract_brain = stats.attack.scale(
            scalar=3.5,
            damage_type=DamageType.Piercing,
            attack_type=AttackType.MeleeNatural,
            die=Die.d10,
            replaces_multiattack=4,
            custom_target=f"one dazed humanoid grappled by {stats.selfref}",
            additional_description=f"If this damage reduces the target to 0 hit points, {stats.selfref} kills the target \
                by extracting and devouring its brain.",
            name="Extract Brain",
        )

        stats = stats.add_attack(extract_brain)

        return stats, stunning_tentacles


DissonantWhispers: Power = _DissonantWhispers()
ExtractBrain: Power = _ExtractBrain()
MindBlast: Power = _MindBlast()
PsychicInfestation: Power = _PsychicInfestation()
PsychicMirror: Power = _PsychicMirror()
Telekinetic: Power = _Telekinetic()

PsychicPowers: List[Power] = [
    DissonantWhispers,
    ExtractBrain,
    MindBlast,
    PsychicInfestation,
    PsychicMirror,
    Telekinetic,
]

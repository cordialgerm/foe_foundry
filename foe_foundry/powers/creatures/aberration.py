from math import floor
from typing import List, Tuple

import numpy as np

from foe_foundry.features import Feature
from foe_foundry.statblocks import BaseStatblock

from ...creature_types import CreatureType
from ...damage import AttackType, Condition
from ...features import ActionType, Feature
from ...statblocks import BaseStatblock
from ..power import Power, PowerType
from ..scores import (
    EXTRA_HIGH_AFFINITY,
    HIGH_AFFINITY,
    LOW_AFFINITY,
    MODERATE_AFFINITY,
    NO_AFFINITY,
)


class _GraspingTentacles(Power):
    """Grasping Tentacles (Reaction). When this creature hits with an attack,
    they sprout a tentacle that grasps the target. In addition to the attack's normal effects, the target is grappled (escape
    DC = 11 + 1/2 CR) and restrained. Until the grapple ends, this creature can't use the grappling tentacle against another
    target. This creature can sprout 1d4 tentacles."""

    def __init__(self):
        super().__init__(name="Grasping Tentacles", power_type=PowerType.Creature)

    def score(self, candidate: BaseStatblock) -> float:
        if candidate.creature_type != CreatureType.Aberration:
            return NO_AFFINITY

        return (
            EXTRA_HIGH_AFFINITY
            if candidate.attack_type == AttackType.MeleeNatural
            else MODERATE_AFFINITY
        )

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature]:
        dc = int(floor(11 + 0.5 * stats.cr))
        feature = Feature(
            name="Grasping Tentacles",
            description=f"On a hit, the target sprouts a tentacle that grapples the target (escape DC {dc}). While grappled in this way, the target is restrained.",
            action=ActionType.Feature,
            modifies_attack=True,
            hidden=True,
        )
        return stats, feature


class _DominatingGaze(Power):
    """Dominating Gaze (Action, Recharge 4-6). If this creature has the multiattack action, Dominating Gaze can take the place of
    one of the attacks used in that action. This creature chooses a target they can see within 60 feet of them. The target must
    succeed on a Charisma saving throw (DC = 12 + 1/2 CR) or be forced to immediately make their most effective weapon attack or at-will spell or magical attack against a target chosen
    by this creature."""

    def __init__(self):
        super().__init__(name="Dominating Gaze", power_type=PowerType.Creature)

    def score(self, candidate: BaseStatblock) -> float:
        if candidate.creature_type != CreatureType.Aberration:
            return NO_AFFINITY

        return (
            EXTRA_HIGH_AFFINITY
            if candidate.attack_type == AttackType.RangedSpell
            else MODERATE_AFFINITY
        )

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature]:
        dc = int(floor(12 + 0.5 * stats.cr))
        feature = Feature(
            name="Dominating Gaze",
            action=ActionType.Action,
            recharge=4,
            replaces_multiattack=1,
            description=f"One target of this creature's choice that they can see within 60 feet must succed on a DC {dc} Charisma saving throw \
                or be forced to immediately use their reaction to make their most effective weapon attack or at-will spell or magical attack against a target chosen by this creature. \
                This counts as a **Charm** effect.",
        )
        return stats, feature


class _MaddeningWhispers(Power):
    def __init__(self):
        super().__init__(name="Maddening Whispers", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        if candidate.creature_type != CreatureType.Aberration:
            return NO_AFFINITY

        return HIGH_AFFINITY

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature]:
        dc = stats.difficulty_class_easy
        feature = Feature(
            name="Madenning Whispers",
            action=ActionType.Feature,
            description=f"Each creature that starts its turn within 20 ft of {stats.selfref} must make a DC {dc} Wisdom saving throw. \
                On a failure, the creature can't take reactions until the start of its next turn and rolls a d8 to determine what it does during its turn. \
                On a 1-4, the creature does nothing. On a 5-6, the creature takes no action or bonus action and uses all its movement to move in a randomly determined direction. \
                On a 7-8, the creature makes a melee attack against a randomly determined creature within its reach or does nothing if it can't make such an attack.",
        )

        return stats, feature


GraspingTentacles: Power = _GraspingTentacles()
DominatingGaze: Power = _DominatingGaze()
MadenningWhispers: Power = _MaddeningWhispers()

AberrationPowers: List[Power] = [GraspingTentacles, DominatingGaze, MadenningWhispers]

# TODO - future options
# Eye Beams
# Mind Blast & Brain Eating
# Chaotic Regeneration (Slaad)
# Mind-Shattering Whispers (Cloaker, Gibbering Mouther)
# Enslave (Aboleth)

from math import floor
from typing import List, Tuple

from foe_foundry.features import Feature
from foe_foundry.statblocks import BaseStatblock

from ...creature_types import CreatureType
from ...damage import AttackType
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

    def apply(self, stats: BaseStatblock) -> Tuple[BaseStatblock, Feature]:
        # TODO - integrate this directly into the attack via an AttackTemplate

        dc = int(floor(11 + 0.5 * stats.cr))
        feature = Feature(
            name="Grasping Tentacles",
            description=f"When this creature hits with an attack, they sprout a tentacle that grasps the target. \
                In addition to the attack's normal effects, the target is grappled (escape DC {dc}) and restrained.",
            action=ActionType.Reaction,
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

    def apply(self, stats: BaseStatblock) -> Tuple[BaseStatblock, Feature]:
        dc = int(floor(12 + 0.5 * stats.cr))
        feature = Feature(
            name="Dominating Gaze",
            action=ActionType.Action,
            recharge=4,
            replaces_multiattack=1,
            description=f"One target of this creature's choice that they can see within 60 feet must succed on a DC {dc} Charisma saving throw \
                or be forced to immediately use their reaction to make their most effective weapon attack or at-will spell or magical attack against a target chosen by this creature.",
        )
        return stats, feature


GraspingTentacles: Power = _GraspingTentacles()
DominatingGaze: Power = _DominatingGaze()

AberrationPowers: List[Power] = [GraspingTentacles, DominatingGaze]

# TODO - future options
# Eye Beams
# Mind Blast & Brain Eating
# Chaotic Regeneration (Slaad)
# Mind-Shattering Whispers (Cloaker, Gibbering Mouther)
# Enslave (Aboleth)

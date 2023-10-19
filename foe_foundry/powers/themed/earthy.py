from math import ceil, floor
from typing import List, Tuple

from numpy.random import Generator

from ...attributes import Skills, Stats
from ...creature_types import CreatureType
from ...damage import AttackType, DamageType
from ...features import ActionType, Feature
from ...powers.power_type import PowerType
from ...role_types import MonsterRole
from ...size import Size
from ...statblocks import BaseStatblock, MonsterDials
from ..power import LOW_POWER, Power, PowerBackport, PowerType
from ..scores import (
    EXTRA_HIGH_AFFINITY,
    HIGH_AFFINITY,
    LOW_AFFINITY,
    MODERATE_AFFINITY,
    NO_AFFINITY,
)


class _Burrower(PowerBackport):
    def __init__(self):
        super().__init__(name="Burrower", power_type=PowerType.Theme, power_level=LOW_POWER)

    def score(self, candidate: BaseStatblock) -> float:
        score = LOW_AFFINITY
        if candidate.creature_type in {CreatureType.Beast, CreatureType.Monstrosity}:
            score += EXTRA_HIGH_AFFINITY
        return score

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        new_speed = stats.speed.copy(burrow=stats.speed.walk)
        new_senses = stats.senses.copy(blindsight=60)
        stats = stats.copy(speed=new_speed, senses=new_senses)

        tunnel_width = 10 if stats.size >= Size.Huge else 5

        feature = Feature(
            name="Burrower",
            action=ActionType.Feature,
            description=f"{stats.selfref.capitalize()} can burrow through solid rock at half its burrow speed and leaves a {tunnel_width} foot wide diameter tunnel in its wake.",
        )

        return stats, feature


class _Climber(PowerBackport):
    def __init__(self):
        super().__init__(name="Climber", power_type=PowerType.Theme, power_level=LOW_POWER)

    def score(self, candidate: BaseStatblock) -> float:
        score = LOW_AFFINITY
        if candidate.creature_type in {
            CreatureType.Beast,
            CreatureType.Monstrosity,
            CreatureType.Ooze,
        }:
            score += EXTRA_HIGH_AFFINITY
        if candidate.role in {MonsterRole.Artillery, MonsterRole.Ambusher}:
            score += MODERATE_AFFINITY
        return score

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        new_speed = stats.speed.copy(climb=stats.speed.walk)
        new_attrs = stats.attributes.grant_proficiency_or_expertise(
            Skills.Athletics, Skills.Acrobatics
        )
        stats = stats.copy(speed=new_speed, attributes=new_attrs)

        ## Spider Climb
        if stats.creature_type in {
            CreatureType.Beast,
            CreatureType.Monstrosity,
            CreatureType.Ooze,
        }:
            feature = Feature(
                name="Spider Climb",
                action=ActionType.Feature,
                description=f"{stats.selfref.capitalize()} can climb difficult surfaces, including upside down on ceilings, without needing to make an ability check",
            )
        else:
            feature = Feature(
                name="Climber",
                action=ActionType.Feature,
                hidden=True,
                description=f"{stats.selfref.capitalize()} gains a climb speed equal to its walk speed",
            )

        return stats, feature


class _Stoneskin(PowerBackport):
    def __init__(self):
        super().__init__(name="Stoneskin", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        if candidate.creature_type == CreatureType.Giant:
            return HIGH_AFFINITY
        elif candidate.creature_type == CreatureType.Monstrosity:
            return MODERATE_AFFINITY
        elif candidate.creature_type == CreatureType.Dragon:
            return MODERATE_AFFINITY
        elif (
            candidate.creature_type == CreatureType.Elemental
            and candidate.secondary_damage_type not in {DamageType.Lightning}
        ):
            return HIGH_AFFINITY
        else:
            return NO_AFFINITY

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        feature = Feature(
            name="Stoneskin",
            action=ActionType.Reaction,
            recharge=5,
            description=f"{stats.selfref.capitalize()} instantly hardens its exterior in response to being hit by an attack. \
                {stats.selfref.capitalize()} gains resistance to non-psychic damage until the end of its next turn",
        )

        return stats, feature


Burrower: Power = _Burrower()
Climber: Power = _Climber()
Stoneskin: Power = _Stoneskin()

EarthyPowers: List[Power] = [Burrower, Climber, Stoneskin]

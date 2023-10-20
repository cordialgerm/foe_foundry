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
from ..scoring import score


def score_earthy(candidate: BaseStatblock, **args) -> float:
    return score(
        candidate=candidate,
        require_types=[CreatureType.Beast, CreatureType.Monstrosity, CreatureType.Ooze],
        **args,
    )


class _Burrower(PowerBackport):
    def __init__(self):
        super().__init__(name="Burrower", power_type=PowerType.Theme, power_level=LOW_POWER)

    def score(self, candidate: BaseStatblock) -> float:
        return score_earthy(candidate)

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
        return score_earthy(
            candidate, bonus_roles=[MonsterRole.Artillery, MonsterRole.Ambusher]
        )

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


Burrower: Power = _Burrower()
Climber: Power = _Climber()

EarthyPowers: List[Power] = [Burrower, Climber]

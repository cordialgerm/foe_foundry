from datetime import datetime
from math import ceil, floor
from typing import List, Tuple

import numpy as np
from numpy.random import Generator

from foe_foundry.features import Feature
from foe_foundry.statblocks import BaseStatblock

from ...attributes import Skills, Stats
from ...creature_types import CreatureType
from ...damage import AttackType, Bleeding, DamageType, Weakened
from ...die import Die, DieFormula
from ...features import ActionType, Feature
from ...powers import PowerType
from ...role_types import MonsterRole
from ...size import Size
from ...statblocks import BaseStatblock, MonsterDials
from ...utils import easy_multiple_of_five, summoning
from ..power import (
    HIGH_POWER,
    LOW_POWER,
    MEDIUM_POWER,
    Power,
    PowerType,
    PowerWithStandardScoring,
)
from ..scoring import score


def score_chaotic(candidate: BaseStatblock, min_cr: float | None = None, **args) -> float:
    return score(
        candidate=candidate,
        require_types=[CreatureType.Fey, CreatureType.Aberration, CreatureType.Monstrosity],
        bonus_attack_types=AttackType.AllSpell(),
        require_cr=min_cr,
        **args,
    )


class ChaoticPower(PowerWithStandardScoring):
    def __init__(
        self,
        name: str,
        source: str,
        power_level: float = MEDIUM_POWER,
        create_date: datetime | None = None,
        **score_args,
    ):
        standard_score_args = dict(
            require_types=[CreatureType.Fey, CreatureType.Aberration, CreatureType.Monstrosity],
            bonus_attack_types=AttackType.AllSpell(),
            **score_args,
        )
        super().__init__(
            name=name,
            power_type=PowerType.Theme,
            source=source,
            theme="Chaotic",
            create_date=create_date,
            power_level=power_level,
            score_args=standard_score_args,
        )


class _ChaoticSpace(ChaoticPower):
    def __init__(self):
        super().__init__(
            name="Chaotic Space",
            source="FoeFoundryOriginal",
            power_level=LOW_POWER,
            require_cr=5,
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class
        radius = easy_multiple_of_five(stats.cr * 5, min_val=10, max_val=45)
        distance = 30 if stats.cr <= 5 else 60

        feature = Feature(
            name="Chaotic Space",
            action=ActionType.Action,
            uses=1,
            replaces_multiattack=1,
            description=f"{stats.selfref.capitalize()} creates a region of chaotic space in a {radius} foot sphere centered at a point it can see within {distance} feet. \
                Whenever another creature casts a spell within this space, it must make a DC {dc} Charisma saving throw or trigger a *Wild Magic Surge*. \
                Whenever another creature ends its turn within the space, it teleports 30 (1d10 x 5) feet in a random direction.",
        )

        return [feature]


class _EldritchBeacon(ChaoticPower):
    def __init__(self):
        super().__init__(
            name="Eldritch Beacon",
            source="FoeFoundryOriginal",
            power_level=HIGH_POWER,
            require_cr=5,
            require_callback=self.can_summon,
        )

    def can_summon(self, c: BaseStatblock) -> bool:
        return self._summon_formula(c, np.random.default_rng(20210518)) is not None

    def _summon_formula(self, stats: BaseStatblock, rng: Generator) -> str | None:
        try:
            summon_cr_target = stats.cr / 5
            _, _, description = summoning.determine_summon_formula(
                summoner=stats.creature_type, summon_cr_target=summon_cr_target, rng=rng
            )
            return description
        except:
            return None

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        hp = easy_multiple_of_five(stats.cr * 5, min_val=5, max_val=30)
        ac = 10
        duration = DieFormula.from_expression("1d4 + 1")
        description = self._summon_formula(stats, np.random.default_rng(20210518))

        feature = Feature(
            name="Eldritch Beacon",
            action=ActionType.Action,
            uses=1,
            replaces_multiattack=2,
            description=f"{stats.selfref.capitalize()} magically creates an Eldritch Beacon (hp {hp}, AC {ac}) at an unoccupied space it can see within 30 feet. \
                Each turn that the beacon is active, on initiative count 0, {description} \
                After {duration.description} rounds the beacon is destroyed.",
        )
        return [feature]


ChaoticSpace: Power = _ChaoticSpace()
EldritchBeacon: Power = _EldritchBeacon()

ChaoticPowers: List[Power] = [ChaoticSpace, EldritchBeacon]

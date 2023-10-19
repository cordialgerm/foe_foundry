from math import ceil
from typing import List, Tuple

import numpy as np

from ...features import ActionType, Feature
from ...role_types import MonsterRole
from ...size import Size
from ...skills import Skills, Stats
from ...statblocks import BaseStatblock
from ...utils.rounding import easy_multiple_of_five
from ..power import HIGH_POWER, LOW_POWER, Power, PowerBackport, PowerType
from ..utils import score


def score_leader(candidate: BaseStatblock) -> float:
    return score(
        candidate=candidate,
        require_roles=MonsterRole.Leader,
        require_stats=Stats.CHA,
        bonus_skills=[Skills.Persuasion, Skills.Intimidation, Skills.Insight],
        bonus_stats=[Stats.CHA, Stats.INT, Stats.WIS],
    )


class _ShoutOrders(PowerBackport):
    def __init__(self):
        super().__init__(name="Shout Orders", power_type=PowerType.Role, power_level=HIGH_POWER)

    def score(self, candidate: BaseStatblock) -> float:
        return score_leader(candidate)

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature]:
        feature = Feature(
            name="Shout Orders",
            description=f"{stats.roleref.capitalize()} chooses up to six creatures who can see and hear them. \
                          Those creatures can immediately either move their speed or make an attack.",
            action=ActionType.BonusAction,
            recharge=4,
        )
        return stats, feature


class _Intimidate(PowerBackport):
    def __init__(self):
        super().__init__(name="Intimidate", power_type=PowerType.Role)

    def score(self, candidate: BaseStatblock) -> float:
        return score_leader(candidate)

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature]:
        new_attrs = stats.attributes.grant_proficiency_or_expertise(Skills.Intimidation)
        stats = stats.copy(attributes=new_attrs)

        feature = Feature(
            name="Intimidate",
            action=ActionType.BonusAction,
            recharge=5,
            description=f"{stats.roleref.capitalize()} chooses a target that can hear them within 50 ft. \
                The target must make a contested Insight check against {stats.roleref}'s Intimidation. \
                On a failure, the target is **Frightened** of {stats.roleref} for 1 minute (save ends at end of turn).\
                While Frightened in this way, attacks made against the target have advantage.",
        )

        return stats, feature


class _Encouragement(PowerBackport):
    def __init__(self):
        super().__init__(name="Encouragement", power_type=PowerType.Role)

    def score(self, candidate: BaseStatblock) -> float:
        return score_leader(candidate)

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature]:
        new_attributes = stats.attributes.grant_proficiency_or_expertise(
            Skills.Medicine, Skills.Insight
        )
        stats = stats.copy(attributes=new_attributes)
        hp = easy_multiple_of_five(
            int(stats.attributes.stat_mod(Stats.WIS) + max(5, ceil(stats.cr * 2)))
        )

        feature = Feature(
            name="Encouragement",
            description=f"{stats.roleref.capitalize()} encourages another creature within 50 feet. \
                The chosen creature gains {hp} temporary hitpoints and may repeat a saving throw against any negative condition affecting them, ending that condition on a success.",
            action=ActionType.BonusAction,
        )

        return stats, feature


class _LeadByExample(PowerBackport):
    def __init__(self):
        super().__init__(name="Lead by Example", power_type=PowerType.Role)

    def score(self, candidate: BaseStatblock) -> float:
        return score_leader(candidate)

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature]:
        feature = Feature(
            name="Lead by Example",
            description=f"On a hit, any of {stats.roleref}'s allies gain advantage on attack rolls against the target until the start of {stats.roleref}'s next turn.",
            action=ActionType.Feature,
            modifies_attack=True,
            hidden=True,
        )
        return stats, feature


class _Reposition(PowerBackport):
    """Each ally within 60 feet of this creature who can see and hear them
    can immediately move their speed without provoking opportunity attacks."""

    def __init__(self):
        super().__init__(name="Reposition", power_type=PowerType.Theme, power_level=LOW_POWER)

    def score(self, candidate: BaseStatblock) -> float:
        return score_leader(candidate)

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature]:
        feature = Feature(
            name="Reposition",
            description=f"Each ally within 60 ft that can see and hear {stats.selfref} \
                can immediately move its speed without provoking opportunity attacks",
            action=ActionType.BonusAction,
            recharge=5,
        )
        return stats, feature


ShoutOrders: Power = _ShoutOrders()
Intimidate: Power = _Intimidate()
Encouragement: Power = _Encouragement()
LeadByExample: Power = _LeadByExample()
Reposition: Power = _Reposition()


LeaderPowers: List[Power] = [ShoutOrders, Intimidate, Encouragement, LeadByExample, Reposition]

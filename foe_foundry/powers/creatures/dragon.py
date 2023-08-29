from math import ceil, floor
from typing import List, Tuple

from numpy.random import Generator

from foe_foundry.features import Feature
from foe_foundry.powers.power_type import PowerType
from foe_foundry.statblocks import BaseStatblock

from ...attributes import Skills, Stats
from ...creature_types import CreatureType
from ...damage import AttackType
from ...features import ActionType, Feature
from ...statblocks import BaseStatblock, MonsterDials
from ..power import Power, PowerType
from ..scores import (
    EXTRA_HIGH_AFFINITY,
    HIGH_AFFINITY,
    LOW_AFFINITY,
    MODERATE_AFFINITY,
    NO_AFFINITY,
)


class _DragonsGaze(Power):
    def __init__(self):
        super().__init__(name="Dragon's Gaze", power_type=PowerType.Creature)

    def score(self, candidate: BaseStatblock) -> float:
        if candidate.creature_type != CreatureType.Dragon:
            return NO_AFFINITY

        return HIGH_AFFINITY

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        new_attrs = stats.attributes.grant_proficiency_or_expertise(Skills.Stealth)
        stats = stats.copy(attributes=new_attrs)

        dc = stats.difficulty_class
        dmg = int(max(3, stats.cr / 2))

        feature = Feature(
            name="Dragon's Gaze",
            action=ActionType.BonusAction,
            recharge=6,
            description=f"One creature within 60 feet of {stats.selfref} must make a DC {dc} Wisdom save or be frightened of {stats.selfref}. \
                While frightened in this way, each time the target takes damage, they take an additional {dmg} damage. Save ends at end of turn.",
        )

        return stats, feature


class _DraconicRetaliation(Power):
    def __init__(self):
        super().__init__(name="Draconic Retaliation", power_type=PowerType.Creature)

    def score(self, candidate: BaseStatblock) -> float:
        if candidate.creature_type != CreatureType.Dragon:
            return NO_AFFINITY

        score = LOW_AFFINITY

        if candidate.cr >= 5:
            score += HIGH_AFFINITY

        return score

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, Feature | List[Feature]]:
        hp = int(floor(stats.hp.average / 2))
        uses = 1
        description = f"When {stats.selfref} is reduced to {hp} hit points or fewer, it may immediately use either its breath weapon or Multiattack action. \
            If {stats.selfref} is incapacitated or otherwise unable to use this trait, it may use it the next time they are able."

        if stats.cr >= 15:
            uses = 2
            hp2 = int(ceil(hp / 2))
            description += f" {stats.selfref.capitalize()} may activate this ability again when reduced to {hp2} hit points or fewer."

        feature = Feature(
            name="Draconic Retaliation",
            action=ActionType.Reaction,
            uses=uses,
            description=description,
        )

        return stats, feature


DragonsGaze: Power = _DragonsGaze()
DraconicRetaliation: Power = _DraconicRetaliation()


DragonPowers: List[Power] = [DragonsGaze, DraconicRetaliation]

from datetime import datetime
from typing import List

from foe_foundry.references import feature_ref

from ...attack_template import natural
from ...creature_types import CreatureType
from ...damage import Condition, DamageType
from ...features import ActionType, Feature
from ...power_types import PowerType
from ...statblocks import BaseStatblock
from .. import flags
from ..power import (
    HIGH_POWER,
    Power,
    PowerCategory,
    PowerWithStandardScoring,
)


class _PetrifyingPower(PowerWithStandardScoring):
    def __init__(
        self,
        name: str,
        icon: str,
        power_level: float = HIGH_POWER,
        reference_statblock="Gorgon",
        power_types: List[PowerType] | None = None,
        **score_args,
    ):
        super().__init__(
            name=name,
            source="Foe Foundry",
            theme="petrifying",
            reference_statblock=reference_statblock,
            icon=icon,
            power_level=power_level,
            power_category=PowerCategory.Theme,
            power_types=power_types or [PowerType.Debuff, PowerType.Attack],
            create_date=datetime(2025, 3, 14),
            score_args=dict(
                bonus_types=CreatureType.Monstrosity,
                bonus_damage=DamageType.Poison,
                require_flags=flags.PETRIFYING,
            )
            | score_args,
        )

    def modify_stats_inner(self, stats: BaseStatblock) -> BaseStatblock:
        stats = super().modify_stats_inner(stats)
        return stats.with_flags(flags.PETRIFYING)


def _petrification(stats: BaseStatblock) -> Feature:
    petrified = Condition.Petrified
    restrained = Condition.Restrained
    dc = stats.difficulty_class_easy
    feature = Feature(
        name="Petrification",
        action=ActionType.Feature,
        description=f"{stats.selfref.capitalize()} can turn creatures to stone. When affected, the creature must succeed on a DC {dc} Constitution saving throw or be {restrained.caption}. \
                At the end of its next turn, the creature repeats the save. If it fails, it is {petrified.caption}.",
    )
    return feature


class _PetrifyingGaze(_PetrifyingPower):
    def __init__(
        self,
    ):
        super().__init__(
            name="Petrifying Gaze",
            icon="medusa-head",
            reference_statblock="Basilisk",
            power_types=[PowerType.Debuff],
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        petrification = _petrification(stats)

        feature = Feature(
            name="Petrifying Gaze",
            action=ActionType.BonusAction,
            recharge=4,
            description=f"Each creature in a 30-foot cone is affected by the {stats.selfref}'s {feature_ref(petrification.name)}",
        )

        return [petrification, feature]


class _PetrifyingGlance(_PetrifyingPower):
    def __init__(self):
        super().__init__(
            name="Petrifying Glance",
            icon="medusa-head",
            reference_statblock="Basilisk",
            power_types=[PowerType.Debuff, PowerType.Attack],
        )

    def modify_stats(self, stats: BaseStatblock) -> BaseStatblock:
        stats = super().modify_stats(stats)

        if isinstance(stats.reaction_count, int) and stats.reaction_count < 3:
            stats = stats.copy(reaction_count=3)

        return stats

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        petrification = _petrification(stats)
        feature = Feature(
            name="Petrifying Glance",
            action=ActionType.Reaction,
            description=f"If a creature within 60 feet looks at {stats.selfref} (such as to make an attack or target it with a spell or ability), then {stats.selfref} uses {feature_ref(petrification.name)} on that creature.",
        )

        return [petrification, feature]


class _PetrifyingBite(_PetrifyingPower):
    def __init__(self):
        super().__init__(
            name="Petrifying Bite",
            icon="sharp-lips",
            attack_names={"-", natural.Bite},
            power_types=[PowerType.Debuff, PowerType.Attack],
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        petrification = _petrification(stats)
        feature = Feature(
            name="Petrifying Bite",
            action=ActionType.Feature,
            modifies_attack=True,
            hidden=True,
            description=f"On a hit, the target must save or be affected by {feature_ref(petrification.name)}.",
        )
        return [petrification, feature]


PetrifyingGaze: Power = _PetrifyingGaze()
PetrifyingGlance = _PetrifyingGlance()
PetrifyingBite = _PetrifyingBite()

PetrifyingPowers: list[Power] = [PetrifyingGaze, PetrifyingGlance, PetrifyingBite]

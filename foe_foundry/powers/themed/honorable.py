from datetime import datetime
from typing import List

from foe_foundry.utils import easy_multiple_of_five

from ...creature_types import CreatureType
from ...damage import AttackType
from ...features import ActionType, Feature
from ...role_types import MonsterRole
from ...statblocks import BaseStatblock
from .. import flags
from ..power import (
    MEDIUM_POWER,
    Power,
    PowerType,
    PowerWithStandardScoring,
)


def could_be_honorable(stats: BaseStatblock) -> bool:
    if stats.creature_type != CreatureType.Humanoid:
        return False

    allowed_roles = {MonsterRole.Soldier, MonsterRole.Leader}
    if not len(allowed_roles.intersection(stats.additional_roles)):
        return False

    wis_score = stats.attributes.WIS >= 12
    cha_score = stats.attributes.CHA >= 12

    score = wis_score + cha_score
    return score >= 2


class HonorablePower(PowerWithStandardScoring):
    def __init__(
        self,
        name: str,
        source: str = "Foe Foundry",
        power_level: float = MEDIUM_POWER,
        create_date: datetime | None = datetime(2025, 3, 22),
        **score_args,
    ):
        super().__init__(
            name=name,
            source=source,
            power_type=PowerType.Theme,
            power_level=power_level,
            theme="honorable",
            create_date=create_date,
            score_args=dict(
                require_callback=could_be_honorable,
                require_types=CreatureType.Humanoid,
                require_attack_types=AttackType.AllMelee(),
                require_roles={
                    MonsterRole.Soldier,
                    MonsterRole.Leader,
                },
            )
            | score_args,
        )


class _Challenge(HonorablePower):
    def __init__(self):
        super().__init__(
            name="Challenge",
            power_level=MEDIUM_POWER,
            require_no_flags=flags.HAS_DUEL,
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Challenge",
            action=ActionType.Action,
            replaces_multiattack=1,
            description=f"{stats.selfref.capitalize()} challenges another creature within 30 feet to the duel. The duel concludes when one of the targets is reduced to 0 hit points, is incapacitated, or dies. \
                Any creature not part of the duel has disadvantage on attack rolls against {stats.selfref} and {stats.selfref} has advantage on any saves against effects or abilities caused by any creature not in the duel. \
                {stats.selfref.capitalize()} may only have one active duel at a time.",
        )
        return [feature]

    def modify_stats_inner(self, stats: BaseStatblock) -> BaseStatblock:
        return super().modify_stats_inner(stats).with_flags(flags.HAS_DUEL)


class _HonorboundDuelist(HonorablePower):
    def __init__(self):
        super().__init__(
            name="Honorbound Duelist",
            power_level=MEDIUM_POWER,
            require_no_flags=flags.HAS_DUEL,
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Honorbound Duelist",
            action=ActionType.Feature,
            description=f"{stats.selfref.capitalize()} has advantage on d20 tests as long as there is exactly one enemy and no other ally within 10 feet",
        )
        return [feature]

    def modify_stats_inner(self, stats: BaseStatblock) -> BaseStatblock:
        return super().modify_stats_inner(stats).with_flags(flags.HAS_DUEL)


class _MortalVow(HonorablePower):
    def __init__(self):
        super().__init__(
            name="Mortal Vow",
            power_level=MEDIUM_POWER,
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        temp_hp = easy_multiple_of_five(stats.hp.average * 0.4, min_val=5)
        feature = Feature(
            name="Mortal Vow",
            action=ActionType.Feature,
            description=f"{stats.selfref.capitalize()} has sworn a sacred vow. If the vow is threatened or violated by an enemy, {stats.selfref} immediately gains {temp_hp} temp hp and takes an additional turn after the current turn ends.",
        )
        return [feature]

    def modify_stats_inner(self, stats: BaseStatblock) -> BaseStatblock:
        return super().modify_stats_inner(stats).with_flags(flags.HAS_DUEL)


Challenge: Power = _Challenge()
HonorboundDuelist: Power = _HonorboundDuelist()
MortalVow: Power = _MortalVow()

HonorablePowers: list[Power] = [Challenge, HonorboundDuelist, MortalVow]

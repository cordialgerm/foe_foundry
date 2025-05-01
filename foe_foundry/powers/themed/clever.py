from datetime import datetime
from math import ceil
from typing import List

from ...attributes import Skills, Stats
from ...creature_types import CreatureType
from ...damage import AttackType
from ...die import DieFormula
from ...features import ActionType, Feature
from ...role_types import MonsterRole
from ...spells import CasterType, evocation
from ...statblocks import BaseStatblock
from ...utils import easy_multiple_of_five
from ..power import LOW_POWER, MEDIUM_POWER, Power, PowerType, PowerWithStandardScoring


class CleverPower(PowerWithStandardScoring):
    def __init__(
        self,
        name: str,
        source: str,
        power_level: float = MEDIUM_POWER,
        create_date: datetime | None = None,
        reference_statblock: str = "Spy",
        **score_args,
    ):
        standard_score_args = dict(
            require_types=CreatureType.all_but(CreatureType.Beast),
            require_stats=[Stats.INT, Stats.WIS, Stats.CHA],
            bonus_roles=[MonsterRole.Leader, MonsterRole.Controller],
            stat_threshold=16,
            **score_args,
        )
        super().__init__(
            name=name,
            power_level=power_level,
            power_type=PowerType.Theme,
            source=source,
            theme="clever",
            reference_statblock=reference_statblock,
            create_date=create_date,
            score_args=standard_score_args,
        )


class _IdentifyWeakness(CleverPower):
    def __init__(self):
        super().__init__(
            name="Identify Weakness", source="Foe Foundry", power_level=LOW_POWER
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Identify Weakness",
            action=ActionType.Reaction,
            description=f"When an ally that {stats.selfref} can see misses an attack against a hostile target, {stats.selfref} can make an Investigation check with a DC equal to the hostile target's AC. \
                On a success, the attack hits instead of missing.",
        )
        return [feature]

    def modify_stats_inner(self, stats: BaseStatblock) -> BaseStatblock:
        stats = super().modify_stats_inner(stats)

        new_attrs = (
            stats.attributes.boost(Stats.CHA, 2)
            .boost(Stats.INT, 2)
            .boost(Stats.WIS, 2)
            .grant_proficiency_or_expertise(Skills.Investigation, Skills.Perception)
            .grant_save_proficiency(Stats.INT)
        )
        stats = stats.copy(attributes=new_attrs)
        return stats


class _ArcaneMark(CleverPower):
    def __init__(self):
        super().__init__(
            name="Arcane Mark",
            source="SRD5.1 Faerie Fire",
            create_date=datetime(2023, 11, 24),
            require_attack_types=AttackType.RangedSpell,
            bonus_types=CreatureType.Fey,
            power_level=LOW_POWER,
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Arcane Mark",
            uses=1,
            action=ActionType.BonusAction,
            description=f"Immediately after hitting a target with a ranged attack, {stats.selfref} casts *Faerie Fire* centered on the target.",
        )
        return [feature]

    def modify_stats_inner(self, stats: BaseStatblock) -> BaseStatblock:
        stats = super().modify_stats_inner(stats)
        stats = stats.grant_spellcasting(CasterType.Arcane)
        return stats.add_spell(evocation.FaerieFire.for_statblock())


class _UnsettlingWords(CleverPower):
    def __init__(self):
        super().__init__(name="Unsettling Words", source="Foe Foundry")

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        uses = ceil(stats.cr / 7)
        distance = easy_multiple_of_five(5 + 1.25 * stats.cr, min_val=10, max_val=30)

        if stats.cr <= 5:
            die = DieFormula.from_expression("1d4")
        elif stats.cr <= 11:
            die = DieFormula.from_expression("1d6")
        else:
            die = DieFormula.from_expression("1d8")

        feature = Feature(
            name="Unsettling Words",
            action=ActionType.Reaction,
            uses=uses,
            description=f"Whenever a hostile creature within {distance} ft that can hear {stats.selfref} makes a d20 ability check, \
                {stats.selfref} can roll {die} and subtract the result from the total, potentially turning a success into a failure",
        )
        return [feature]


ArcaneMark: Power = _ArcaneMark()
IdentifyWeaknes: Power = _IdentifyWeakness()
UnsettlingWords: Power = _UnsettlingWords()


CleverPowers: List[Power] = [ArcaneMark, IdentifyWeaknes, UnsettlingWords]

from datetime import datetime
from typing import List

from foe_foundry.utils import easy_multiple_of_five

from ...creature_types import CreatureType
from ...damage import AttackType
from ...features import ActionType, Feature
from ...power_types import PowerType
from ...role_types import MonsterRole
from ...skills import Skills
from ...statblocks import BaseStatblock
from ..power import (
    MEDIUM_POWER,
    Power,
    PowerCategory,
    PowerWithStandardScoring,
)


def could_be_hunter(stats: BaseStatblock) -> bool:
    # Allow giants, beasts, or monsters with high WIS or STR
    allowed_types = {CreatureType.Giant, CreatureType.Beast, CreatureType.Monstrosity}
    if stats.creature_type not in allowed_types:
        return False
    wis_score = stats.attributes.WIS >= 12
    str_score = stats.attributes.STR >= 16
    return wis_score or str_score


class HunterPower(PowerWithStandardScoring):
    def __init__(
        self,
        name: str,
        icon: str,
        source: str = "Foe Foundry",
        power_level: float = MEDIUM_POWER,
        create_date: datetime | None = datetime(2025, 7, 17),
        power_types: List[PowerType] | None = None,
        **score_args,
    ):
        super().__init__(
            name=name,
            source=source,
            power_category=PowerCategory.Theme,
            power_level=power_level,
            icon=icon,
            theme="hunter",
            reference_statblock="Frost Giant",
            create_date=create_date,
            power_types=power_types or [PowerType.Buff, PowerType.Attack],
            score_args=dict(
                require_callback=could_be_hunter,
                require_types={
                    CreatureType.Giant,
                    CreatureType.Beast,
                    CreatureType.Monstrosity,
                },
                require_attack_types=AttackType.AllMelee(),
                require_roles={MonsterRole.Soldier, MonsterRole.Bruiser},
            )
            | score_args,
        )


class _GloryOfTheHunt(HunterPower):
    def __init__(self):
        super().__init__(
            name="Glory of the Hunt",
            icon="hunting-horn",
            power_level=MEDIUM_POWER,
            power_types=[PowerType.Buff],
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        temp_hp = easy_multiple_of_five(stats.hp.average * 0.1, min_val=5)
        dc = 8 + (
            stats.attributes.skill_mod(Skills.Insight, even_if_not_proficient=True) or 0
        )
        feature = Feature(
            name="Glory of the Hunt",
            action=ActionType.BonusAction,
            description=(
                f"{stats.selfref} boasts about its most legendary kill, granting itself {temp_hp} temporary hit points and advantage on attacks until the start of its next turn. "
                f"If an opponent can truthfully boast of a more impressive kill or successfully deceive {stats.selfref} (DC {dc} Deception check), then {stats.selfref} loses the temporary hit points, has disadvantage on d20 tests until the end of its next turn, and can no longer use this ability."
            ),
        )
        return [feature]

    def modify_stats_inner(self, stats: BaseStatblock) -> BaseStatblock:
        return stats


GloryOfTheHunt: Power = _GloryOfTheHunt()

HunterPowers: list[Power] = [GloryOfTheHunt]

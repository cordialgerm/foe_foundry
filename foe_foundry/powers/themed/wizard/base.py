from datetime import datetime
from typing import List

from foe_foundry.features import Feature
from foe_foundry.statblocks import BaseStatblock

from ....damage import AttackType
from ....spells import StatblockSpell
from ...power import HIGH_POWER, PowerType, PowerWithStandardScoring


class _Wizard(PowerWithStandardScoring):
    def __init__(
        self,
        name: str,
        creature_class: str,
        min_cr: int,
        max_cr: int,
        spells: List[StatblockSpell],
        theme: str,
        score_args: dict,
    ):
        score_args = (
            dict(
                require_cr=min_cr,
                require_max_cr=max_cr,
                require_attack_types=AttackType.AllSpell(),
            )
            | score_args
        )

        super().__init__(
            name=name,
            power_type=PowerType.Theme,
            source="SRD5.1",
            theme=theme,
            power_level=HIGH_POWER,
            create_date=datetime(2023, 12, 14),
            score_args=score_args,
        )

        self.spells = spells
        self.creature_class = creature_class

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        return []

    def modify_stats(self, stats: BaseStatblock) -> BaseStatblock:
        stats = stats.copy(creature_class=self.creature_class)
        return stats.add_spells(self.spells)

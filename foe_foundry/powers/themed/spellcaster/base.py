from datetime import datetime
from typing import List

from foe_foundry.features import Feature
from foe_foundry.statblocks import BaseStatblock

from ....damage import AttackType
from ....spells import StatblockSpell
from ...power import HIGH_POWER, PowerType, PowerWithStandardScoring


class _Spellcaster(PowerWithStandardScoring):
    def __init__(
        self,
        name: str,
        spells: List[StatblockSpell],
        theme: str,
        score_args: dict,
        min_cr: int = 1,
        max_cr: int = 100,
        creature_class: str | None = None,
        power_level=HIGH_POWER,
        require_attack_types=AttackType.AllSpell(),
    ):
        score_args = (
            dict(
                require_cr=min_cr,
                require_max_cr=max_cr,
                require_attack_types=require_attack_types,
            )
            | score_args
        )

        super().__init__(
            name=name,
            power_type=PowerType.Spellcasting,
            source="FoeFoundry",
            theme=theme,
            power_level=power_level,
            create_date=datetime(2023, 12, 14),
            score_args=score_args,
        )

        self.spells = spells
        self.creature_class = creature_class

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        return []

    def modify_stats(self, stats: BaseStatblock) -> BaseStatblock:
        if self.creature_class is not None and stats.creature_class is None:
            stats = stats.copy(creature_class=self.creature_class)
        sorted_spells = sorted(self.spells, key=lambda s: s.name)
        return stats.add_spells(sorted_spells)

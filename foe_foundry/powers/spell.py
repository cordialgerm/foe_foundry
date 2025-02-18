from typing import List

from ..features import Feature
from ..spells import StatblockSpell
from ..statblocks import BaseStatblock
from .power import MEDIUM_POWER, PowerType, PowerWithStandardScoring


class SpellPower(PowerWithStandardScoring):
    def __init__(
        self,
        spell: StatblockSpell,
        theme: str,
        score_args: dict,
        **kwargs,
    ):
        power_level = kwargs.get("power_level", MEDIUM_POWER)
        kwargs.pop("power_level", None)

        if "require_cr" not in score_args:
            score_args.update(require_cr=spell.recommended_min_cr)

        if "name" not in kwargs:
            kwargs.update(name=f"Spellcasting - {spell.name}")

        if "source" not in kwargs:
            kwargs.update(source="SRD 5.1")

        super().__init__(
            power_type=PowerType.Spellcasting,
            theme=theme,
            score_args=score_args,
            power_level=power_level,
            **kwargs,
        )
        self.spell = spell

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        return []

    def modify_stats(self, stats: BaseStatblock) -> BaseStatblock:
        return stats.add_spell(spell=self.spell.copy())

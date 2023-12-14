import math
from typing import List

from num2words import num2words

from foe_foundry.statblocks import BaseStatblock

from ..features import ActionType, Feature
from ..spells import StatblockSpell
from ..statblocks import BaseStatblock
from .power import MEDIUM_POWER, PowerType, PowerWithStandardScoring


class SpellPower(PowerWithStandardScoring):
    def __init__(
        self,
        spell: StatblockSpell,
        power_type: PowerType,
        theme: str,
        score_args: dict,
        **kwargs,
    ):
        power_level = kwargs.get("power_level", MEDIUM_POWER)
        kwargs.pop("power_level", None)

        if "require_cr" not in score_args:
            score_args.update(require_cr=_min_cr_for_spell(spell, power_level))

        if "name" not in kwargs:
            kwargs.update(name=f"Spellcasting - {spell.name}")

        if "source" not in kwargs:
            kwargs.update(source="SRD 5.1")

        super().__init__(
            power_type=power_type,
            theme=theme,
            score_args=score_args,
            power_level=power_level,
            **kwargs,
        )
        self.spell = spell

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        return []

    def modify_stats(self, stats: BaseStatblock) -> BaseStatblock:
        spell = self.spell
        if spell.uses is None:
            cr_surplus = max(stats.cr - _min_cr_for_spell(spell, self.power_level), 0)
            uses = min(3, max(1, math.ceil(cr_surplus / 3)))
            spell = spell.copy(uses=uses)

        return stats.add_spell(spell=spell)


def _min_cr_for_spell(spell: StatblockSpell, power_level: float) -> float:
    return spell.level * 1.5 * power_level

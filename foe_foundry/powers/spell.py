from typing import List

from ..features import Feature
from ..spells import CasterType, StatblockSpell
from ..statblocks import BaseStatblock
from .power import MEDIUM_POWER, PowerType, PowerWithStandardScoring


class SpellPower(PowerWithStandardScoring):
    def __init__(
        self,
        spell: StatblockSpell,
        caster_type: CasterType,
        theme: str,
        score_args: dict,
        icon: str,
        **kwargs,
    ):
        power_level = kwargs.get("power_level", MEDIUM_POWER)
        kwargs.pop("power_level", None)

        if "require_cr" not in score_args:
            score_args.update(require_cr=spell.recommended_min_cr)

        if "name" not in kwargs:
            kwargs.update(name=f"Spellcasting-{spell.name}")

        if "source" not in kwargs:
            kwargs.update(source="SRD 5.1")

        super().__init__(
            power_type=PowerType.Spellcasting,
            theme=theme,
            score_args=score_args,
            power_level=power_level,
            icon=icon,
            **kwargs,
        )
        self.spell = spell
        self.caster_type = caster_type

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        return []

    def modify_stats_inner(self, stats: BaseStatblock) -> BaseStatblock:
        stats = stats.grant_spellcasting(self.caster_type)
        return stats.add_spell(spell=self.spell.copy())

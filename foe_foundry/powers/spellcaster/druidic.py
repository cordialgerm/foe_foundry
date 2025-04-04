from typing import List

from ...creature_types import CreatureType
from ...spells import CasterType, StatblockSpell, conjuration, evocation, transmutation
from ..power import Power
from .base import _Spellcaster
from .utils import spell_list

_adept = [
    conjuration.Entangle.copy(concentration=False),
    evocation.FaerieFire.copy(concentration=False),
    evocation.Moonbeam,
]
_master = [evocation.IceStorm, transmutation.PlantGrowth]
_expert = [evocation.Sunburst, transmutation.ReverseGravity]

DruidicAdeptSpells = spell_list(spells=_adept, uses=1)
DruidicSpells = spell_list(
    spells=_adept,
    uses=1,
) + spell_list(spells=_master, uses=1)
DruidicExpertSpells = spell_list(spells=_adept + _master + _expert, uses=1)


class _Druidic(_Spellcaster):
    def __init__(
        self, name: str, spells: List[StatblockSpell], min_cr: int, max_cr: int
    ):
        super().__init__(
            name=name,
            spells=spells,
            caster_type=CasterType.Primal,
            theme="druidic",
            min_cr=min_cr,
            max_cr=max_cr,
            score_args=dict(require_types=[CreatureType.Humanoid]),
        )


DruidicAdeptPower: Power = _Druidic(
    name="Druid Adept", min_cr=1, max_cr=2, spells=DruidicAdeptSpells
)
DruidicMasterPower: Power = _Druidic(
    name="Druid", min_cr=3, max_cr=8, spells=DruidicSpells
)
DruidicExpertPower: Power = _Druidic(
    name="Druidic Expert", min_cr=9, max_cr=99, spells=DruidicExpertSpells
)

DruidicPowers: list[Power] = [
    DruidicAdeptPower,
    DruidicMasterPower,
    DruidicExpertPower,
]

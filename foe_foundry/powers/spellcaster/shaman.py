from typing import List

from ...creature_types import CreatureType
from ...power_types import PowerType
from ...spells import (
    CasterType,
    StatblockSpell,
    conjuration,
    enchantment,
    evocation,
    illusion,
    necromancy,
)
from ..power import Power
from .base import _Spellcaster
from .utils import spell_list

_adept = [
    conjuration.Entangle.copy(concentration=False),
    evocation.FaerieFire.copy(concentration=False),
    conjuration.SleetStorm,
    necromancy.BestowCurse,
]
_shaman = [conjuration.CallLightning, necromancy.Blight]

ShamanAdeptSpells = spell_list(spells=_adept, uses=1)
ShamanSpells = spell_list(
    spells=_adept, uses=1, exclude={conjuration.SleetStorm}
) + spell_list(spells=_shaman, uses=1)

OniTricksterSpells = spell_list(
    spells=[
        evocation.LightningBolt,
        illusion.GreaterInvisibility,
        enchantment.CharmPerson,
    ],
    uses=1,
)


class _Shaman(_Spellcaster):
    def __init__(
        self, name: str, spells: List[StatblockSpell], min_cr: int, max_cr: int
    ):
        super().__init__(
            name=name,
            spells=spells,
            caster_type=CasterType.Primal,
            theme="shaman",
            reference_statblock="Druid",
            icon="totem",
            min_cr=min_cr,
            max_cr=max_cr,
            power_types=[PowerType.Magic],
            score_args=dict(require_types=[CreatureType.Humanoid]),
        )


ShamanAdeptPower: Power = _Shaman(
    name="Shaman Adept", min_cr=1, max_cr=2, spells=ShamanAdeptSpells
)

ShamanPower: Power = _Shaman(name="Shaman", min_cr=3, max_cr=8, spells=ShamanSpells)


OniTrickster: Power = _Shaman(
    name="Oni Trickster", min_cr=7, max_cr=10, spells=OniTricksterSpells
)


ShamanPowers: list[Power] = [ShamanAdeptPower, ShamanPower, OniTrickster]

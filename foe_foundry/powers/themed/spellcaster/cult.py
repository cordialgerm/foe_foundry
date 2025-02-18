from typing import List

from ....damage import AttackType
from ....spells import enchantment, evocation, necromancy
from ....statblocks import BaseStatblock
from ...power import HIGH_POWER, MEDIUM_POWER, Power
from .base import _Spellcaster
from .utils import spell_list

_adept = [enchantment.Command, enchantment.HoldPerson]
_master = [evocation.MassCureWounds, evocation.FlameStrike]
_expert = [enchantment.MassSuggestion, necromancy.FingerOfDeath]

CultAdeptSpells = spell_list(_adept, uses=1)
CultMasterSpells = spell_list(_adept, uses=1) + spell_list(_master, uses=1)
CultExpertSpells = (
    spell_list(_adept, uses=1)
    + spell_list(_master, uses=1)
    + spell_list(_expert, uses=1)
)


def is_cultist(c: BaseStatblock):
    return c.creature_class and "cult" in c.creature_class.lower()


class _CultCaster(_Spellcaster):
    def __init__(self, **kwargs):
        args: dict = (
            dict(
                theme="cult",
                score_args=dict(
                    require_attack_types=AttackType.AllSpell(),
                    require_callback=is_cultist,
                ),
            )
            | kwargs
        )

        super().__init__(**args)


def CultCasters() -> List[Power]:
    return [
        _CultCaster(
            name="Cult Spellcasting Adept",
            min_cr=2,
            max_cr=4,
            spells=CultAdeptSpells,
            power_level=MEDIUM_POWER,
        ),
        _CultCaster(
            name="Cult Spellcasting Master",
            min_cr=5,
            max_cr=10,
            spells=CultMasterSpells,
            power_level=HIGH_POWER,
        ),
        _CultCaster(
            name="Cult Spellcasting Expert",
            min_cr=11,
            max_cr=40,
            spells=CultExpertSpells,
            power_level=HIGH_POWER,
        ),
    ]

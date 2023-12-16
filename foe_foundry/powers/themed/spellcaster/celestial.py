from typing import List

from ....creature_types import CreatureType
from ....damage import AttackType
from ....role_types import MonsterRole
from ....spells import abjuration, divination, evocation, necromancy, transmutation
from ...power import HIGH_POWER, LOW_POWER, Power
from .base import _Spellcaster
from .utils import spell_list

_adept = [
    divination.DetectEvilAndGood,
    divination.Commune,
    abjuration.LesserRestoration,
    necromancy.RaiseDead,
]
_master = [
    abjuration.DispelMagic,
    abjuration.GreaterRestoration,
    abjuration.DispelEvilAndGood,
    evocation.FlameStrike,
    evocation.MassCureWounds,
]
_expert = [evocation.BladeBarrier, necromancy.Resurrection, transmutation.ControlWeather]

CelestialAdeptSpells = spell_list(_adept, uses=1)
CelestialMasterSpells = spell_list(
    _adept, uses=2, exclude={abjuration.LesserRestoration}
) + spell_list(_master, uses=1)
CelestialExpertSpells = (
    spell_list(_adept, uses=3, exclude={abjuration.LesserRestoration, necromancy.RaiseDead})
    + spell_list(_master, uses=2)
    + spell_list(_expert, uses=1)
)


class _CelestialCaster(_Spellcaster):
    def __init__(self, **kwargs):
        args: dict = (
            dict(
                theme="celestial",
                score_args=dict(
                    require_types=[
                        CreatureType.Celestial,
                    ],
                    require_attack_types=None,  # overwrite requirement in base class
                    bonus_attack_types=AttackType.AllSpell(),
                    bonus_roles=[MonsterRole.Defender, MonsterRole.Leader],
                ),
            )
            | kwargs
        )

        super().__init__(**args)


def CelestialCasters() -> List[Power]:
    return [
        _CelestialCaster(
            name="Celestial Adept",
            min_cr=2,
            max_cr=4,
            spells=CelestialAdeptSpells,
            power_level=LOW_POWER,
        ),
        _CelestialCaster(
            name="Celestial Master",
            min_cr=5,
            max_cr=10,
            spells=CelestialMasterSpells,
            power_level=HIGH_POWER,
        ),
        _CelestialCaster(
            name="Celestial Expert",
            min_cr=11,
            max_cr=40,
            spells=CelestialExpertSpells,
            power_level=HIGH_POWER,
        ),
    ]

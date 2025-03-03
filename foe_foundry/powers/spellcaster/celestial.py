from typing import List

from ...creature_types import CreatureType
from ...damage import AttackType, DamageType
from ...role_types import MonsterRole
from ...spells import abjuration, divination, evocation, necromancy
from ...statblocks import BaseStatblock
from ..power import HIGH_POWER, LOW_POWER, Power
from .base import _Spellcaster
from .utils import spell_list

_adept = [
    divination.DetectEvilAndGood,
    abjuration.CureWounds,
    abjuration.LesserRestoration,
    abjuration.DispelMagic,
]
_master = [
    abjuration.GreaterRestoration,
    abjuration.DispelEvilAndGood,
    abjuration.MassCureWounds,
]
_expert = [
    evocation.FlameStrike,
    abjuration.Heal,
    necromancy.Resurrection,
]

CelestialAdeptSpells = spell_list(_adept, uses=1, exclude={abjuration.CureWounds})
CelestialMasterSpells = spell_list(
    _adept, uses=2, exclude={abjuration.LesserRestoration}
) + spell_list(_master, uses=1, exclude={divination.DetectEvilAndGood})
CelestialExpertSpells = (
    spell_list(
        _adept,
        uses=3,
        exclude={
            abjuration.LesserRestoration,
            divination.DetectEvilAndGood,
            necromancy.RaiseDead,
        },
    )
    + spell_list(_master, uses=2)
    + spell_list(_expert, uses=1)
)


def is_celestial_caster(stats: BaseStatblock) -> bool:
    return stats.creature_type == CreatureType.Celestial or (
        stats.creature_type == CreatureType.Humanoid
        and stats.secondary_damage_type == DamageType.Radiant
    )


class _CelestialCaster(_Spellcaster):
    def __init__(self, **kwargs):
        args: dict = (
            dict(
                theme="Celestial",
                score_args=dict(
                    require_callback=is_celestial_caster,
                    require_types=[CreatureType.Celestial, CreatureType.Humanoid],
                    require_attack_types=None,  # overwrite requirement in base class
                    bonus_attack_types=AttackType.AllSpell(),
                    bonus_roles=[
                        MonsterRole.Defender,
                        MonsterRole.Leader,
                        MonsterRole.Soldier,
                        MonsterRole.Support,
                    ],
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

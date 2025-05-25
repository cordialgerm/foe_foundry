from ...creature_types import CreatureType
from ...damage import AttackType, DamageType
from ...role_types import MonsterRole
from ...spells import CasterType, abjuration, divination, evocation, necromancy
from ...statblocks import BaseStatblock
from ..power import HIGH_POWER, LOW_POWER, Power
from .base import _Spellcaster
from .utils import spell_list

_initiate = [abjuration.CureWounds]
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

CelestialInitiateSpells = spell_list(_initiate, uses=1)
CelestialAdeptSpells = spell_list(_adept, uses=1)
CelestialMasterSpells = spell_list(
    _adept,
    uses=1,
    exclude={
        abjuration.LesserRestoration,
        abjuration.CureWounds,
        divination.DetectEvilAndGood,
    },
) + spell_list(_master, uses=1)
CelestialExpertSpells = (
    spell_list(
        _adept,
        uses=1,
        exclude={
            abjuration.LesserRestoration,
            abjuration.CureWounds,
            divination.DetectEvilAndGood,
        },
    )
    + spell_list(_master, uses=1)
    + spell_list(_expert, uses=1)
)


def is_celestial_caster(stats: BaseStatblock) -> bool:
    return stats.creature_type == CreatureType.Celestial or (
        stats.creature_type == CreatureType.Humanoid
        and (
            stats.secondary_damage_type == DamageType.Radiant
            or stats.caster_type == CasterType.Divine
        )
    )


class _CelestialCaster(_Spellcaster):
    def __init__(self, **kwargs):
        args: dict = (
            dict(
                theme="Celestial",
                reference_statblock="Deva",
                icon="angel-wings",
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
                caster_type=CasterType.Divine,
            )
            | kwargs
        )

        super().__init__(**args)


CelestialInitiate: Power = _CelestialCaster(
    name="Celestial Initiate",
    min_cr=0,
    max_cr=1,
    spells=CelestialInitiateSpells,
    power_level=LOW_POWER,
)
CelestialAdept: Power = _CelestialCaster(
    name="Celestial Adept",
    min_cr=2,
    max_cr=4,
    spells=CelestialAdeptSpells,
    power_level=LOW_POWER,
)
CelestialMaster: Power = _CelestialCaster(
    name="Celestial Master",
    min_cr=5,
    max_cr=10,
    spells=CelestialMasterSpells,
    power_level=HIGH_POWER,
)
CelestialExpert: Power = _CelestialCaster(
    name="Celestial Expert",
    min_cr=11,
    max_cr=40,
    spells=CelestialExpertSpells,
    power_level=HIGH_POWER,
)


CelestialCasters: list[Power] = [
    CelestialAdept,
    CelestialMaster,
    CelestialExpert,
]

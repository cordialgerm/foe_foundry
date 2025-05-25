from ...creature_types import CreatureType
from ...damage import AttackType
from ...role_types import MonsterRole
from ...spells import (
    CasterType,
    abjuration,
    enchantment,
    evocation,
    illusion,
    necromancy,
)
from ..power import HIGH_POWER, LOW_POWER, Power
from .base import _Spellcaster
from .utils import spell_list

_adept = [
    abjuration.DispelMagic,
    evocation.Darkness,
    illusion.Fear,
    enchantment.Suggestion,
]
_master = [evocation.WallOfFire, evocation.Fireball]
_expert = [necromancy.FingerOfDeath, necromancy.CircleOfDeath]

FiendishAdeptSpells = spell_list(_adept, uses=1)
FiendishMasterSpells = spell_list(_adept, uses=2) + spell_list(_master, uses=1)
FiendishExpertSpells = (
    spell_list(_adept, uses=3)
    + spell_list(_master, uses=2)
    + spell_list(_expert, uses=1)
)


class _FiendishCaster(_Spellcaster):
    def __init__(self, **kwargs):
        args: dict = (
            dict(
                theme="fiend",
                caster_type=CasterType.Innate,
                reference_statblock="Cambion",
                icon="evil-fork",
                score_args=dict(
                    require_types=[
                        CreatureType.Fiend,
                    ],
                    require_attack_types=None,  # overwrite requirement in base class
                    bonus_attack_types=AttackType.AllSpell(),
                    bonus_roles=[
                        MonsterRole.Artillery,
                        MonsterRole.Controller,
                        MonsterRole.Leader,
                    ],
                ),
            )
            | kwargs
        )

        super().__init__(**args)


FiendishAdept = _FiendishCaster(
    name="Fiendish Adept",
    min_cr=2,
    max_cr=4,
    spells=FiendishAdeptSpells,
    power_level=LOW_POWER,
)
FiendishMaster = _FiendishCaster(
    name="Fiendish Master",
    min_cr=5,
    max_cr=10,
    spells=FiendishMasterSpells,
    power_level=HIGH_POWER,
)
FiendishExpert = _FiendishCaster(
    name="Fiendish Expert",
    min_cr=11,
    max_cr=40,
    spells=FiendishExpertSpells,
    power_level=HIGH_POWER,
)

FiendishSpellcasters = [
    FiendishAdept,
    FiendishMaster,
    FiendishExpert,
]


def spellcaster_for_cr(cr: float) -> Power | None:
    """
    Returns the appropriate spellcaster for a given CR.
    """
    if cr < 2:
        return None
    elif cr <= 4:
        return FiendishAdept
    elif cr <= 10:
        return FiendishMaster
    else:
        return FiendishExpert

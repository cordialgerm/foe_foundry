from typing import List

from ....creature_types import CreatureType
from ....damage import DamageType, conditions
from ....die import Die
from ....features import ActionType, Feature
from ....spells import enchantment, illusion, transmutation
from ....statblocks import BaseStatblock
from ...power import HIGH_POWER, MEDIUM_POWER, Power
from .base import _Spellcaster
from .utils import spell_list

_adept = [illusion.Fear]
_master = [transmutation.Telekinesis]
_expert = [enchantment.Feeblemind]

PsionicAdeptSpells = spell_list(_adept, uses=1)
PsionicMasterSpells = spell_list(_adept, uses=1) + spell_list(_master, uses=1)
PsionicExpertSpells = (
    spell_list(_adept, uses=1)
    + spell_list(_master, uses=1)
    + spell_list(_expert, uses=1)
)


class _PsionicCaster(_Spellcaster):
    def __init__(self, **kwargs):
        args: dict = (
            dict(
                theme="psionic",
                creature_class="Psion",
                score_args=dict(
                    require_no_creature_class=True,
                    require_damage=DamageType.Psychic,
                    require_damage_exact_match=True,
                    bonus_types=CreatureType.Aberration,
                ),
            )
            | kwargs
        )

        super().__init__(**args)

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        damage = stats.target_value(1.25, force_die=Die.d6)
        dazed = conditions.Dazed()
        dc = stats.difficulty_class

        feature = Feature(
            name="Mind Lash",
            action=ActionType.Action,
            recharge=5,
            replaces_multiattack=2,
            description=f"{stats.roleref.capitalize()} lashes out with psionic energy at a creature it can see within 60 feet of it. The target must succeed on a DC {dc} Intelligence saving throw. \
                On a failure, the target suffers {damage.description} psychic damage and is {dazed.caption} until the end of its next turn. {dazed.description_3rd}",
        )

        return [feature]


def PsionicCasters() -> List[Power]:
    return [
        _PsionicCaster(
            name="Psionic Adept",
            min_cr=2,
            max_cr=4,
            spells=PsionicAdeptSpells,
            power_level=MEDIUM_POWER,
        ),
        _PsionicCaster(
            name="Psionic Master",
            min_cr=5,
            max_cr=10,
            spells=PsionicMasterSpells,
            power_level=HIGH_POWER,
        ),
        _PsionicCaster(
            name="Psionic Expert",
            min_cr=11,
            max_cr=40,
            spells=PsionicExpertSpells,
            power_level=HIGH_POWER,
        ),
    ]

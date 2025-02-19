from typing import List

from ....attack_template import spell
from ....creature_types import CreatureType
from ....damage import DamageType
from ....features import ActionType, Feature
from ....role_types import MonsterRole
from ....spells import (
    conjuration,
    divination,
    enchantment,
    evocation,
    illusion,
    transmutation,
)
from ....statblocks import BaseStatblock
from ...power import EXTRA_HIGH_POWER, HIGH_POWER, MEDIUM_POWER
from .base import _Spellcaster
from .utils import spell_list

_adept = [
    divination.DetectMagic,
    divination.DetectThoughts,
    divination.ArcaneEye,
    illusion.Invisibility,
    enchantment.HoldPerson,
    transmutation.Fly,
]
_master = [
    evocation.LightningBolt,
    divination.Scrying,
    illusion.GreaterInvisibility,
]
_expert = [conjuration.Maze, divination.Foresight]

DivinationAdeptSpells = spell_list(_adept, uses=1)
DivinationMasterSpells = spell_list(
    _adept, uses=2, exclude={illusion.Invisibility}
) + spell_list(_master, uses=1)
DivinationExpertSpells = (
    spell_list(_adept, uses=3, exclude={illusion.Invisibility})
    + spell_list(_master, uses=2)
    + spell_list(_expert, uses=1)
)


class _DivinationWizard(_Spellcaster):
    def __init__(self, **kwargs):
        args: dict = (
            dict(
                creature_class="Diviner",
                theme="divination",
                score_args=dict(
                    require_types=[
                        CreatureType.Humanoid,
                        CreatureType.Fey,
                        CreatureType.Celestial,
                        CreatureType.Aberration,
                    ],
                    bonus_damage=DamageType.Psychic,
                    bonus_roles=MonsterRole.Controller,
                    attack_names=[
                        spell.Gaze,
                        spell.EldritchBlast,
                        spell.ArcaneBurst,
                    ],  # bonus, not required
                ),
            )
            | kwargs
        )

        super().__init__(**args)

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Portent of Weal and Woe",
            action=ActionType.Reaction,
            uses=2,
            description=f"When another creature the {stats.roleref} can see within 60 feet makes a d20 test, {stats.roleref} can replace the result of the roll with a 5 or a 15.",
        )
        return [feature]


def DivinationWizards() -> List[_Spellcaster]:
    return [
        _DivinationWizard(
            name="Diviniation Adept",
            min_cr=2,
            max_cr=4,
            spells=DivinationAdeptSpells,
            power_level=MEDIUM_POWER,
        ),
        _DivinationWizard(
            name="Divination Master",
            min_cr=5,
            max_cr=10,
            spells=DivinationMasterSpells,
            power_level=HIGH_POWER,
        ),
        _DivinationWizard(
            name="Diviniation Expert",
            min_cr=11,
            max_cr=40,
            spells=DivinationExpertSpells,
            power_level=EXTRA_HIGH_POWER,
        ),
    ]

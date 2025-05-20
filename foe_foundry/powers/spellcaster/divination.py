from typing import List

from ...features import ActionType, Feature
from ...spells import (
    conjuration,
    divination,
    enchantment,
    evocation,
    illusion,
    transmutation,
)
from ...statblocks import BaseStatblock
from ..power import Power
from .base import WizardPower
from .utils import spell_list

_adept = [
    divination.DetectMagic,
    divination.DetectThoughts.copy(concentration=False),
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


class _DivinationWizard(WizardPower):
    def __init__(self, **kwargs):
        super().__init__(creature_name="Diviner", icon="crystal-ball", **kwargs)

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Portent of Weal and Woe",
            action=ActionType.Feature,
            uses=2,
            description=f"When another creature {stats.roleref} can see within 60 feet makes a d20 test, {stats.roleref} can replace the result of the roll with a 5 or a 15.",
        )
        return [feature]


def DivinationWizards() -> List[Power]:
    return [
        _DivinationWizard(
            name="Diviniation Adept",
            min_cr=4,
            max_cr=5,
            spells=DivinationAdeptSpells,
        ),
        _DivinationWizard(
            name="Divination Master",
            min_cr=6,
            max_cr=11,
            spells=DivinationMasterSpells,
        ),
        _DivinationWizard(
            name="Diviniation Expert",
            min_cr=12,
            max_cr=40,
            spells=DivinationExpertSpells,
        ),
    ]

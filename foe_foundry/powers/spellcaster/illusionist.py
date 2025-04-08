from typing import List

from ...features import Feature
from ...spells import illusion
from ...statblocks import BaseStatblock
from ..power import Power
from ..themed.illusory import Projection
from .base import WizardPower
from .utils import spell_list

_adept = [
    illusion.Invisibility,
    illusion.SilentImage.copy(concentration=False),
    illusion.DisguiseSelf,
]
_master = [
    illusion.GreaterInvisibility.copy(concentration=False),
    illusion.Fear,
    illusion.MajorImage.copy(concentration=False),
]
_expert = [
    illusion.PhantasmalKiller,
    illusion.ProgrammedIllusion.copy(concentration=False),
]

IllusionistAdeptSpells = spell_list(_adept, uses=1)
IllusionistMasterSpells = spell_list(
    _adept, uses=2, exclude={illusion.Invisibility}
) + spell_list(_master, uses=1)
IllusionistExpertSpells = (
    spell_list(_adept, uses=3, exclude={illusion.Invisibility})
    + spell_list(_master, uses=2)
    + spell_list(_expert, uses=1)
)


class _IllusionistWizard(WizardPower):
    def __init__(self, **kwargs):
        super().__init__(creature_name="Illusionist", **kwargs)

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        return Projection.generate_features(stats)


def IllusionistWizards() -> List[Power]:
    return [
        _IllusionistWizard(
            name="Illusionist Adept",
            min_cr=4,
            max_cr=5,
            spells=IllusionistAdeptSpells,
        ),
        _IllusionistWizard(
            name="Illusionist Master",
            min_cr=6,
            max_cr=11,
            spells=IllusionistMasterSpells,
        ),
        _IllusionistWizard(
            name="Illusionist Expert",
            min_cr=12,
            max_cr=40,
            spells=IllusionistExpertSpells,
        ),
    ]

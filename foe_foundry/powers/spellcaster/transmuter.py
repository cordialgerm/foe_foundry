from typing import List

from ...features import ActionType, Feature
from ...power_types import PowerType
from ...spells import evocation, transmutation
from ...statblocks import BaseStatblock
from ..power import Power
from .base import WizardPower
from .utils import spell_list

_adept = [
    transmutation.Slow,
    evocation.Fireball,
    transmutation.EnlargeReduce.copy(concentration=False),
]
_master = [
    evocation.ArcaneHand,
    transmutation.FleshToStone.copy(concentration=False),
    transmutation.Disintegrate,
]
_expert = [transmutation.TimeStop, transmutation.ReverseGravity]

TransmutationAdeptSpells = spell_list(_adept, uses=1)
TransmutationMasterSpells = spell_list(
    _adept,
    uses=2,
) + spell_list(_master, uses=1)
TransmutationExpertSpells = (
    spell_list(_adept, uses=3)
    + spell_list(_master, uses=2)
    + spell_list(_expert, uses=1)
)


class _TransmutationWizard(WizardPower):
    def __init__(self, **kwargs):
        super().__init__(creature_name="Transmuter", icon="crystalize", power_types=[PowerType.Magic, PowerType.Buff, PowerType.Debuff], **kwargs)

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Spell Transmutation",
            action=ActionType.Feature,
            description=f"{stats.roleref.capitalize()} may change the damage of any spell or spell attack to acid, cold, fire, lightning, or thunder.",
        )
        return [feature]


def TransmutationWizards() -> List[Power]:
    return [
        _TransmutationWizard(
            name="Transmutation Adept",
            min_cr=4,
            max_cr=5,
            spells=TransmutationAdeptSpells,
        ),
        _TransmutationWizard(
            name="Transmutation Master",
            min_cr=6,
            max_cr=11,
            spells=TransmutationMasterSpells,
        ),
        _TransmutationWizard(
            name="Transmutation Expert",
            min_cr=12,
            max_cr=40,
            spells=TransmutationExpertSpells,
        ),
    ]

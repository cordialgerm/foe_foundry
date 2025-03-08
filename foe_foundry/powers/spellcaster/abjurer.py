from typing import List

from ...features import ActionType, Feature
from ...spells import (
    abjuration,
    conjuration,
    enchantment,
    evocation,
    illusion,
    transmutation,
)
from ...statblocks import BaseStatblock
from ...utils import easy_multiple_of_five
from ..power import Power
from .base import WizardPower
from .utils import spell_list

_adept = [
    abjuration.DispelMagic,
    illusion.Invisibility,
    enchantment.HoldPerson,
    transmutation.Fly,
    conjuration.Web,
]
_master = [
    evocation.WallOfForce,
    abjuration.Banishment,
    evocation.LightningBolt,
    conjuration.Web.copy(concentration=False),
]
_expert = [
    evocation.Forcecage,
    abjuration.GlobeOfInvulnerability,
]

AbjurationAdeptSpells = spell_list(_adept, uses=1)
AbjurationMasterSpells = spell_list(
    _adept, uses=2, exclude={illusion.Invisibility, conjuration.Web}
) + spell_list(_master, uses=1)
AbjurationExpertSpells = (
    spell_list(_adept, uses=3, exclude={illusion.Invisibility, conjuration.Web})
    + spell_list(_master, uses=2)
    + spell_list(_expert, uses=1)
)


class _AbjurationWizard(WizardPower):
    def __init__(self, **kwargs):
        super().__init__(creature_name="Abjurer", **kwargs)

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        protection = easy_multiple_of_five(stats.hp.average / 5)

        feature = Feature(
            name="Defensive Wards",
            action=ActionType.Reaction,
            uses=2,
            description=f"When another creature {stats.roleref} can see within 60 feet takes damage, {stats.roleref} can use its reaction to reduce the damage taken by up to {protection}.",
        )

        return [feature]


def AbjurationWizards() -> List[Power]:
    return [
        _AbjurationWizard(
            name="Abjuration Adept",
            min_cr=4,
            max_cr=5,
            spells=AbjurationAdeptSpells,
        ),
        _AbjurationWizard(
            name="Abjuration Master",
            min_cr=6,
            max_cr=11,
            spells=AbjurationMasterSpells,
        ),
        _AbjurationWizard(
            name="Abjuration Expert",
            min_cr=12,
            max_cr=40,
            spells=AbjurationExpertSpells,
        ),
    ]

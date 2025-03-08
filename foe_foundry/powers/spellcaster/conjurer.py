from typing import List

import numpy as np

from ...features import ActionType, Feature
from ...spells import abjuration, conjuration, evocation, necromancy
from ...statblocks import BaseStatblock
from ...utils.summoning import determine_summon_formula
from ..power import EXTRA_HIGH_POWER, HIGH_POWER, MEDIUM_POWER, Power
from .base import WizardPower
from .utils import spell_list

_adept = [conjuration.Grease, conjuration.Web, conjuration.FogCloud]
_master = [conjuration.Cloudkill, conjuration.SleetStorm, evocation.Fireball]
_expert = [conjuration.Gate, evocation.Forcecage]

ConjurationAdeptSpells = spell_list(_adept, uses=1)
ConjurationMasterSpells = spell_list(
    _adept, uses=2, exclude={abjuration.LesserRestoration}
) + spell_list(_master, uses=1)
ConjurationExpertSpells = (
    spell_list(
        _adept, uses=3, exclude={abjuration.LesserRestoration, necromancy.RaiseDead}
    )
    + spell_list(_master, uses=2)
    + spell_list(_expert, uses=1)
)


class _ConjurationWizard(WizardPower):
    def __init__(self, **kwargs):
        super().__init__(creature_name="Conjurer", **kwargs)

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        creature, _, description = determine_summon_formula(
            summoner=stats.creature_type,
            summon_cr_target=stats.cr / 2,
            rng=np.random.default_rng(20210518),
            allow_generic_summons=True,
            max_quantity=4,
        )
        creature = creature.strip("*")

        feature = Feature(
            name=f"Summon {creature.capitalize()}",
            action=ActionType.Action,
            uses=1,
            replaces_multiattack=2,
            description=description,
        )

        return [feature]


def ConjurationWizards() -> List[Power]:
    return [
        _ConjurationWizard(
            name="Conjuration Adept",
            min_cr=4,
            max_cr=5,
            spells=ConjurationAdeptSpells,
        ),
        _ConjurationWizard(
            name="Conjuration Master",
            min_cr=6,
            max_cr=11,
            spells=ConjurationMasterSpells,
        ),
        _ConjurationWizard(
            name="Conjuration Expert",
            min_cr=12,
            max_cr=40,
            spells=ConjurationExpertSpells,
        ),
    ]

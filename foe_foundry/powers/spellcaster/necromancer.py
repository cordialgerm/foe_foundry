from typing import List

from ...features import ActionType, Feature
from ...spells import conjuration, illusion, necromancy
from ...statblocks import BaseStatblock
from ...utils import easy_multiple_of_five
from ..power import Power
from .base import WizardPower
from .utils import spell_list

_adept = [
    necromancy.BestowCurse,
    conjuration.Web,
    necromancy.BlindnessDeafness,
]
_master = [
    conjuration.Cloudkill,
    necromancy.CircleOfDeath,
    illusion.Fear,
]
_expert = [necromancy.Eyebite, necromancy.FingerOfDeath]

NecromancerAdeptSpells = spell_list(spells=_adept, uses=1)
NecromancerMasterSpells = spell_list(spells=_adept, uses=2) + spell_list(
    spells=_master, uses=1
)
NecromancerExpertSpells = (
    spell_list(_adept, uses=3)
    + spell_list(_master, uses=2)
    + spell_list(_expert, uses=1)
)


class _NecromancerWizard(WizardPower):
    def __init__(self, **kwargs):
        super().__init__(creature_name="Necromancer", **kwargs)

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        temphp = easy_multiple_of_five(stats.hp.average / 2.5)
        feature = Feature(
            name="Soul Harvest",
            uses=1,
            action=ActionType.Reaction,
            description=f"Whenever a humanoid creature within 60 feet dies or is reduced to 0 hitpoints, {stats.roleref} gains {temphp} temporary hitpoints.",
        )

        return [feature]


NecromancerAdept: Power = _NecromancerWizard(
    name="Necromancer Adept",
    min_cr=4,
    max_cr=5,
    spells=NecromancerAdeptSpells,
)

NecromancerMaster: Power = _NecromancerWizard(
    name="Necromancer Master",
    min_cr=6,
    max_cr=11,
    spells=NecromancerMasterSpells,
)

NecromancerExpert: Power = _NecromancerWizard(
    name="Necromancer Expert",
    min_cr=12,
    max_cr=40,
    spells=NecromancerExpertSpells,
)

NecromancerWizards: list[Power] = [
    NecromancerAdept,
    NecromancerMaster,
    NecromancerExpert,
]

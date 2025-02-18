from typing import List

from ....creature_types import CreatureType
from ....features import Feature
from ....role_types import MonsterRole
from ....spells import illusion
from ....statblocks import BaseStatblock
from ...power import HIGH_POWER, LOW_POWER, MEDIUM_POWER
from ..tricky import Projection
from .base import _Spellcaster
from .utils import spell_list

_adept = [illusion.Invisibility, illusion.SilentImage, illusion.DisguiseSelf]
_master = [illusion.GreaterInvisibility, illusion.Fear, illusion.MajorImage]
_expert = [illusion.PhantasmalKiller, illusion.ProgrammedIllusion]

IllusionistAdeptSpells = spell_list(_adept, uses=1)
IllusionistMasterSpells = spell_list(
    _adept, uses=2, exclude={illusion.Invisibility}
) + spell_list(_master, uses=1)
IllusionistExpertSpells = (
    spell_list(_adept, uses=3, exclude={illusion.Invisibility})
    + spell_list(_master, uses=2)
    + spell_list(_expert, uses=1)
)


class _IllusionistWizard(_Spellcaster):
    def __init__(self, **kwargs):
        args: dict = (
            dict(
                creature_class="Illusionist",
                theme="illusion",
                score_args=dict(
                    require_no_creature_class=True,
                    require_types=[
                        CreatureType.Humanoid,
                        CreatureType.Fey,
                    ],
                    bonus_roles=[MonsterRole.Controller, MonsterRole.Ambusher],
                ),
            )
            | kwargs
        )

        super().__init__(**args)

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        return Projection.generate_features(stats)


def IllusionistWizards() -> List[_Spellcaster]:
    return [
        _IllusionistWizard(
            name="Illusionist Adept",
            min_cr=2,
            max_cr=4,
            spells=IllusionistAdeptSpells,
            power_level=LOW_POWER,
        ),
        _IllusionistWizard(
            name="Illusionist Master",
            min_cr=5,
            max_cr=10,
            spells=IllusionistMasterSpells,
            power_level=MEDIUM_POWER,
        ),
        _IllusionistWizard(
            name="Illusionist Expert",
            min_cr=11,
            max_cr=40,
            spells=IllusionistExpertSpells,
            power_level=HIGH_POWER,
        ),
    ]

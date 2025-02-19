from typing import List

from ....attack_template import spell
from ....creature_types import CreatureType
from ....features import ActionType, Feature
from ....role_types import MonsterRole
from ....spells import abjuration, conjuration, enchantment, evocation, illusion, transmutation
from ....statblocks import BaseStatblock
from ....utils import easy_multiple_of_five
from ...power import EXTRA_HIGH_POWER, HIGH_POWER, MEDIUM_POWER
from .base import _Spellcaster
from .utils import spell_list

_adept = [
    abjuration.DispelMagic,
    illusion.Invisibility,
    enchantment.HoldPerson,
    transmutation.Fly,
    conjuration.Web,
]
_master = [evocation.WallOfForce, abjuration.Banishment, evocation.LightningBolt]
_expert = [
    evocation.Forcecage,
    abjuration.GlobeOfInvulnerability,
]

AbjurationAdeptSpells = spell_list(_adept, uses=1)
AbjurationMasterSpells = spell_list(
    _adept, uses=2, exclude={illusion.Invisibility}
) + spell_list(_master, uses=1)
AbjurationExpertSpells = (
    spell_list(_adept, uses=3, exclude={illusion.Invisibility})
    + spell_list(_master, uses=2)
    + spell_list(_expert, uses=1)
)


class _AbjurationWizard(_Spellcaster):
    def __init__(self, **kwargs):
        args: dict = (
            dict(
                creature_class="Abjurer",
                theme="abjuration",
                score_args=dict(
                    require_types=[
                        CreatureType.Humanoid,
                    ],
                    bonus_roles=[MonsterRole.Controller, MonsterRole.Defender],
                    attack_names=[
                        spell.EldritchBlast,
                        spell.ArcaneBurst,
                    ],  # bonus, not required
                ),
            )
            | kwargs
        )

        super().__init__(**args)

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        protection = easy_multiple_of_five(stats.hp.average / 5)

        feature = Feature(
            name="Defensive Wards",
            action=ActionType.Reaction,
            uses=2,
            description=f"When another creature {stats.roleref} can see within 60 feet takes damage, {stats.roleref} can use its reaction to reduce the damage taken by up to {protection}.",
        )

        return [feature]


def AbjurationWizards() -> List[_Spellcaster]:
    return [
        _AbjurationWizard(
            name="Abjuration Adept",
            min_cr=2,
            max_cr=4,
            spells=AbjurationAdeptSpells,
            power_level=MEDIUM_POWER,
        ),
        _AbjurationWizard(
            name="Abjuration Master",
            min_cr=5,
            max_cr=10,
            spells=AbjurationMasterSpells,
            power_level=HIGH_POWER,
        ),
        _AbjurationWizard(
            name="Abjuration Expert",
            min_cr=11,
            max_cr=40,
            spells=AbjurationExpertSpells,
            power_level=EXTRA_HIGH_POWER,
        ),
    ]

from typing import List

from ...creature_types import CreatureType
from ...features import ActionType, Feature
from ...spells import evocation, transmutation
from ...statblocks import BaseStatblock
from ..attack import DamageType
from ..power import EXTRA_HIGH_POWER, HIGH_POWER, Power
from .base import _Wizard
from .utils import spell_list

_adept = [transmutation.Slow, evocation.Fireball, transmutation.EnlargeReduce]
_master = [evocation.ArcaneHand, transmutation.FleshToStone, transmutation.Disintegrate]
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


def is_transmuter(c: BaseStatblock) -> bool:
    return (
        c.creature_type == CreatureType.Humanoid
        and c.secondary_damage_type != DamageType.Radiant
    )


class _TransmutationWizard(_Wizard):
    def __init__(self, **kwargs):
        args: dict = (
            dict(
                theme="transmutation",
                creature_class="Transmuter",
                score_args=dict(
                    require_callback=is_transmuter,
                    require_types=[CreatureType.Humanoid],
                ),
            )
            | kwargs
        )

        super().__init__(**args)

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Spell Transmutation",
            action=ActionType.Feature,
            description=f"{stats.roleref.capitalize()} may choose to change the damage type of any spell they cast to either acid, cold, fire, lightning, or thunder.",
        )
        return [feature]


def TransmutationWizards() -> List[Power]:
    return [
        _TransmutationWizard(
            name="Transmutation Adept",
            min_cr=2,
            max_cr=4,
            spells=TransmutationAdeptSpells,
            power_level=HIGH_POWER,
        ),
        _TransmutationWizard(
            name="Transmutation Master",
            min_cr=5,
            max_cr=10,
            spells=TransmutationMasterSpells,
            power_level=HIGH_POWER,
        ),
        _TransmutationWizard(
            name="Transmutation Expert",
            min_cr=11,
            max_cr=40,
            spells=TransmutationExpertSpells,
            power_level=EXTRA_HIGH_POWER,
        ),
    ]

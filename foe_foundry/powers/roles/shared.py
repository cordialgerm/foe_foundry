from typing import List

from ...features import ActionType, Feature
from ...powers.power_type import PowerType
from ...role_types import MonsterRole
from ...statblocks import BaseStatblock
from ..power import PowerType, PowerWithStandardScoring


def custom_filter(stats: BaseStatblock) -> bool:
    return not stats.has_unique_movement_manipulation


def NimbleEscape(role: MonsterRole):
    class _NimbleEscape(PowerWithStandardScoring):
        def __init__(self):
            super().__init__(
                name=f"Nimble Escape - {role.name}",
                source="SRD5.1 Goblin",
                power_type=PowerType.Role,
                score_args=dict(require_roles=role, require_callback=custom_filter),
                theme=role.name.capitalize(),
            )

        def generate_features(self, stats: BaseStatblock) -> List[Feature]:
            feature = Feature(
                name="Nimble Escape",
                action=ActionType.BonusAction,
                description=f"{stats.roleref.capitalize()} uses Disengage or Hide.",
            )
            return [feature]

        def modify_stats(self, stats: BaseStatblock) -> BaseStatblock:
            return stats.copy(has_unique_movement_manipulation=True)

    return _NimbleEscape()


def CunningAction(role: MonsterRole):
    class _CunningAction(PowerWithStandardScoring):
        def __init__(self):
            super().__init__(
                name=f"Cunning Action - {role.name}",
                source="SRD5.1 Spy",
                power_type=PowerType.Role,
                theme=role.name.capitalize(),
                score_args=dict(require_roles=role, require_callback=custom_filter),
            )

        def generate_features(self, stats: BaseStatblock) -> List[Feature]:
            feature = Feature(
                name="Cunning Action",
                description=f"{stats.roleref.capitalize()} uses Dash, Disengage, or Hide.",
                action=ActionType.BonusAction,
            )
            return [feature]

        def modify_stats(self, stats: BaseStatblock) -> BaseStatblock:
            return stats.copy(has_unique_movement_manipulation=True)

    return _CunningAction()

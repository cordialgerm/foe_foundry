from typing import List

from ...features import ActionType, Feature
from ...powers.power_type import PowerType
from ...role_types import MonsterRole
from ...statblocks import BaseStatblock
from ..power import PowerType, PowerWithStandardScoring


def NimbleEscape(role: MonsterRole):
    class _NimbleEscape(PowerWithStandardScoring):
        def __init__(self):
            super().__init__(
                name=f"Nimble Escape - {role.name}",
                source="SRD1.2 Goblin",
                power_type=PowerType.Role,
                score_args=dict(require_roles=role),
                theme=role.name.capitalize(),
            )

        def generate_features(self, stats: BaseStatblock) -> List[Feature]:
            feature = Feature(
                name="Nimble Escape",
                action=ActionType.BonusAction,
                description=f"{stats.roleref.capitalize()} uses Disengage or Hide.",
            )
            return [feature]

    return _NimbleEscape()


def CunningAction(role: MonsterRole):
    class _CunningAction(PowerWithStandardScoring):
        def __init__(self):
            super().__init__(
                name=f"Cunning Action - {role.name}",
                source="SRD1.2 Sply",
                power_type=PowerType.Role,
                theme=role.name.capitalize(),
                score_args=dict(require_roles=role),
            )

        def generate_features(self, stats: BaseStatblock) -> List[Feature]:
            feature = Feature(
                name="Cunning Action",
                description=f"{stats.roleref.capitalize()} uses Dash, Disengage, or Hide.",
                action=ActionType.BonusAction,
            )
            return [feature]

    return _CunningAction()

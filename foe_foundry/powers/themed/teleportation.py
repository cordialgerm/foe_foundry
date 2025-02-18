from datetime import datetime
from math import ceil
from typing import List

from ...creature_types import CreatureType
from ...damage import AttackType
from ...features import ActionType, Feature
from ...role_types import MonsterRole
from ...statblocks import BaseStatblock
from ..power import LOW_POWER, MEDIUM_POWER, Power, PowerType, PowerWithStandardScoring


class TeleportationPower(PowerWithStandardScoring):
    def __init__(
        self,
        name: str,
        source: str,
        power_level: float = MEDIUM_POWER,
        create_date: datetime | None = None,
        **score_args,
    ):
        def humanoid_is_caster(c: BaseStatblock) -> bool:
            if c.creature_type == CreatureType.Humanoid:
                return any(t.is_spell() for t in c.attack_types)
            else:
                return True

        super().__init__(
            name=name,
            source=source,
            theme="teleportation",
            power_level=power_level,
            power_type=PowerType.Theme,
            create_date=create_date,
            score_args=dict(
                require_callback=humanoid_is_caster,
                require_types={
                    CreatureType.Fey,
                    CreatureType.Fiend,
                    CreatureType.Aberration,
                    CreatureType.Humanoid,
                },
                require_cr=1,
                bonus_attack_types=AttackType.AllSpell(),
                bonus_roles={MonsterRole.Ambusher, MonsterRole.Controller},
            )
            | score_args,
        )


class _BendSpace(TeleportationPower):
    def __init__(self):
        super().__init__(name="Bend Space", source="Foe Foundry")

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Bend Space",
            action=ActionType.Reaction,
            description=f"When {stats.selfref} would be hit by an attack, it teleports and exchanges position with an ally it can see within 60 feet of it. The ally is then hit by the attack instead.",
        )
        return [feature]


def no_unique_movement(stats: BaseStatblock) -> bool:
    return not stats.has_unique_movement_manipulation


class _MistyStep(TeleportationPower):
    def __init__(self):
        super().__init__(
            name="Misty Step",
            source="SRD5.1 Misty Step",
            power_level=LOW_POWER,
            require_callback=no_unique_movement,
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        distance = 30 if stats.cr <= 7 else 60
        uses = int(min(3, ceil(stats.cr / 3)))

        feature = Feature(
            name="Misty Step",
            action=ActionType.BonusAction,
            uses=uses,
            description=f"{stats.selfref.capitalize()} teleports up to {distance} feet to an unoccupied space it can see.",
        )

        return [feature]

    def modify_stats(self, stats: BaseStatblock) -> BaseStatblock:
        return stats.copy(has_unique_movement_manipulation=True)


class _Scatter(TeleportationPower):
    def __init__(self):
        super().__init__(name="Scatter", source="Foe Foundry")

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        distance = 20 if stats.cr <= 7 else 30
        dc = stats.difficulty_class
        count = int(max(2, ceil(stats.cr / 3)))

        feature = Feature(
            name="Scatter",
            action=ActionType.Action,
            recharge=5,
            replaces_multiattack=1,
            description=f"{stats.selfref.capitalize()} forces up to {count} creatures it can see within {distance} feet to make a DC {dc} Charisma save. \
                On a failure, the target is teleported to an unoccupied space within {4 * distance} feet that {stats.selfref} can see. \
                The space must be on the ground or on a floor.",
        )

        return [feature]


BendSpace: Power = _BendSpace()
MistyStep: Power = _MistyStep()
Scatter: Power = _Scatter()

TeleportationPowers: List[Power] = [BendSpace, MistyStep, Scatter]

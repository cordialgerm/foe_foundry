from math import floor
from typing import List

from ...creature_types import CreatureType
from ...damage import AttackType
from ...features import ActionType, Feature
from ...role_types import MonsterRole
from ...statblocks import BaseStatblock
from ..power import LOW_POWER, Power, PowerType, PowerWithStandardScoring


class _Flyer(PowerWithStandardScoring):
    def __init__(self):
        def not_already_special_movement(c: BaseStatblock) -> bool:
            return (
                not (c.speed.fly or 0) and not (c.speed.climb or 0) and not (c.speed.swim or 0)
            )

        super().__init__(
            name="Flyer",
            source="Foe Foundry",
            theme="flying",
            power_level=LOW_POWER,
            power_type=PowerType.Theme,
            score_args=dict(
                require_types={
                    CreatureType.Dragon,
                    CreatureType.Fiend,
                    CreatureType.Celestial,
                    CreatureType.Aberration,
                    CreatureType.Beast,
                    CreatureType.Monstrosity,
                    CreatureType.Elemental,
                    CreatureType.Fey,
                },
                require_callback=not_already_special_movement,
            ),
        )

    def modify_stats(self, stats: BaseStatblock) -> BaseStatblock:
        speed_change = 10 + 10 * int(floor(stats.cr / 10.0))
        new_speed = stats.speed.delta(speed_change=speed_change)
        new_speed = new_speed.copy(fly=new_speed.walk)
        stats = stats.copy(speed=new_speed)
        return stats

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        speed_change = 10 + 10 * int(floor(stats.cr / 10.0))
        feature = Feature(
            name="Flyer",
            action=ActionType.Feature,
            description=f"{stats.selfref.capitalize()}'s movement speed increases by {speed_change} and it gains a fly speed equal to its walk speed",
            hidden=True,
        )
        return [feature]


class _Flyby(PowerWithStandardScoring):
    def __init__(self):
        super().__init__(
            name="Flyby",
            source="A5E SRD Owl",
            theme="flying",
            power_type=PowerType.Theme,
            power_level=LOW_POWER,
            score_args=dict(require_flying=True),
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Flyby",
            action=ActionType.Feature,
            description=f"{stats.selfref.capitalize()} does not provoke opportunity attacks.",
        )
        return [feature]


class _WingedCharge(PowerWithStandardScoring):
    def __init__(self):
        super().__init__(
            name="Winged Charge",
            source="A5E SRD Chimera",
            theme="flying",
            power_type=PowerType.Theme,
            power_level=LOW_POWER,
            score_args=dict(
                require_flying=True,
                require_types=CreatureType.all_but(CreatureType.Aberration),
                bonus_roles={MonsterRole.Bruiser, MonsterRole.Skirmisher},
                require_attack_types=AttackType.AllMelee(),
            ),
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Winged Charge",
            action=ActionType.Reaction,
            uses=1,
            description=f"{stats.selfref.capitalize()} can use its reaction to fly up to its speed towards a creature that hits it with a ranged attack. \
                If within range, it can then make a melee attack against the attacker.",
        )
        return [feature]


class _WingedRetreat(PowerWithStandardScoring):
    def __init__(self):
        super().__init__(
            name="Winged Retreat",
            source="A5E SRD Vulture",
            theme="flying",
            power_type=PowerType.Theme,
            score_args=dict(
                require_flying=True,
                require_roles={MonsterRole.Skirmisher},
            ),
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Winged Retreat",
            action=ActionType.Reaction,
            description=f"When {stats.selfref} would be hit by a melee attack, it can move 5 feet away from the attacker. If this moves \
                {stats.selfref} out of the attacker's reach, the attacker has disadvantage on its attack.",
        )
        return [feature]


Flyer: Power = _Flyer()
Flyby: Power = _Flyby()
WingedCharge: Power = _WingedCharge()
WingedRetreat: Power = _WingedRetreat()

FlyingPowers: List[Power] = [Flyer, Flyby, WingedCharge, WingedRetreat]

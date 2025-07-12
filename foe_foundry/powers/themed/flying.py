from math import floor
from typing import List

from ...creature_types import CreatureType
from ...damage import AttackType
from ...features import ActionType, Feature
from ...power_types import PowerType
from ...role_types import MonsterRole
from ...statblocks import BaseStatblock
from ..power import LOW_POWER, Power, PowerCategory, PowerWithStandardScoring


class FlyingPower(PowerWithStandardScoring):
    def __init__(
        self,
        name: str,
        source: str,
        icon: str,
        power_level: float = LOW_POWER,
        power_types: List[PowerType] | None = None,
        **score_args,
    ):
        def not_already_special_movement(c: BaseStatblock) -> bool:
            return (
                not (c.speed.fly or 0)
                and not (c.speed.climb or 0)
                and not (c.speed.swim or 0)
            )

        super().__init__(
            name=name,
            source=source,
            theme="flying",
            reference_statblock="Giant Eagle",
            icon=icon,
            power_level=power_level,
            power_category=PowerCategory.Theme,
            power_types=power_types or [PowerType.Movement],
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
            )
            | score_args,
        )

    def modify_stats_inner(self, stats: BaseStatblock) -> BaseStatblock:
        stats = super().modify_stats_inner(stats)
        speed = stats.speed.grant_flying()
        stats = stats.copy(speed=speed)
        return stats


class _Flyer(FlyingPower):
    def __init__(self):
        super().__init__(
            name="Flyer",
            icon="swallow",
            source="Foe Foundry",
            power_types=[PowerType.Movement],
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        speed_change = 10 + 10 * int(floor(stats.cr / 10.0))
        feature = Feature(
            name="Flyer",
            action=ActionType.Feature,
            description=f"{stats.selfref.capitalize()}'s movement speed increases by {speed_change} and it gains a fly speed equal to its walk speed",
            hidden=True,
        )
        return [feature]


class _Flyby(FlyingPower):
    def __init__(self):
        super().__init__(
            name="Flyby",
            icon="crow-dive",
            source="A5E SRD Owl",
            require_flying=True,
            power_types=[PowerType.Movement, PowerType.Utility],
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Flyby",
            action=ActionType.Feature,
            description=f"{stats.selfref.capitalize()} does not provoke opportunity attacks.",
        )
        return [feature]


class _WingedCharge(FlyingPower):
    def __init__(self):
        super().__init__(
            name="Winged Charge",
            source="A5E SRD Chimera",
            icon="griffin-symbol",
            require_flying=True,
            require_types=CreatureType.all_but(CreatureType.Aberration),
            bonus_roles={
                MonsterRole.Soldier,
                MonsterRole.Skirmisher,
                MonsterRole.Bruiser,
            },
            require_attack_types=AttackType.AllMelee(),
            power_types=[PowerType.Movement, PowerType.Attack],
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Winged Charge",
            action=ActionType.Reaction,
            uses=1,
            description=f"{stats.selfref.capitalize()} can use its reaction to fly up to its speed towards a creature that hits it with a ranged attack. \
                If within range, it can then make a melee attack against the attacker.",
        )
        return [feature]


class _WingedRetreat(FlyingPower):
    def __init__(self):
        super().__init__(
            name="Winged Retreat",
            source="A5E SRD Vulture",
            icon="dove",
            require_flying=True,
            require_roles={MonsterRole.Skirmisher},
            power_types=[PowerType.Movement, PowerType.Defense],
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
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

from datetime import datetime
from typing import List

from foe_foundry.references import action_ref

from ...attributes import Stats
from ...creature_types import CreatureType
from ...damage import AttackType, Condition
from ...die import Die
from ...features import ActionType, Feature
from ...role_types import MonsterRole
from ...size import Size
from ...statblocks import BaseStatblock
from ..power import (
    HIGH_POWER,
    LOW_POWER,
    MEDIUM_POWER,
    Power,
    PowerType,
    PowerWithStandardScoring,
)


def is_ground(c: BaseStatblock) -> bool:
    return (c.speed.fly or 0) == 0


class SoldierPower(PowerWithStandardScoring):
    def __init__(
        self,
        name: str,
        source: str,
        icon: str,
        create_date: datetime | None = None,
        power_level: float = MEDIUM_POWER,
        **score_args,
    ):
        standard_score_args = (
            dict(
                require_roles=MonsterRole.Soldier,
                bonus_attack_types=AttackType.AllMelee(),
            )
            | score_args
        )
        super().__init__(
            name=name,
            power_type=PowerType.Role,
            power_level=power_level,
            source=source,
            icon=icon,
            create_date=create_date,
            theme="soldier",
            reference_statblock="Warrior",
            score_args=standard_score_args,
        )


class _Phalanx(SoldierPower):
    def __init__(self):
        super().__init__(
            name="Phalanx",
            icon="spears",
            source="Foe Foundry",
            power_level=MEDIUM_POWER,
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Phalanx",
            description=f"{stats.selfref.capitalize()} gains a +1 bonus to its AC and d20 tests whenever another ally with this trait is within 5 feet.",
            action=ActionType.Feature,
        )
        return [feature]


class _CoordinatedStrike(SoldierPower):
    def __init__(self):
        super().__init__(
            name="Coordinated Strike",
            icon="switch-weapons",
            source="Foe Foundry",
            power_level=MEDIUM_POWER,
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Coordinated Strike",
            description=f"Whenever an ally within 5 feet misses an attack and {stats.selfref} is within 5 feet of the target, {stats.selfref} can use their reaction to make an attack against the target. \
                This ability can only trigger once per round for each such group of allies with this trait.",
            action=ActionType.Reaction,
        )
        return [feature]


class _PackTactics(SoldierPower):
    def __init__(self):
        super().__init__(
            name="Pack Tactics",
            source="SRD5.1 Wolf",
            icon="wolf-head",
            require_types={
                CreatureType.Beast,
                CreatureType.Humanoid,
                CreatureType.Monstrosity,
            },
            bonus_roles={
                MonsterRole.Soldier,
                MonsterRole.Bruiser,
            },
            power_level=HIGH_POWER,
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Pack Tactics",
            action=ActionType.Feature,
            description=f"{stats.selfref.capitalize()} has advantage on attack rolls against a target if at least one of {stats.selfref}'s allies is within 5 feet and isn't incapacitated.",
        )
        return [feature]


class _Disciplined(SoldierPower):
    def __init__(self):
        super().__init__(
            name="Disciplined",
            icon="spartan",
            source="Foe Foundry",
            require_roles=MonsterRole.Soldier,
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Disciplined",
            action=ActionType.Reaction,
            description=f"If {stats.selfref} misses an attack or fails a saving throw while another friendly creature is within 10 feet, it may use its reaction to re-roll the attack or saving throw.",
        )
        return [feature]


class _ActionSurge(SoldierPower):
    def __init__(self):
        super().__init__(
            name="Action Surge",
            icon="attack-gauge",
            source="SRD5.1 Action Surge",
            power_level=HIGH_POWER,
            require_cr=3,
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Action Surge",
            uses=1,
            action=ActionType.BonusAction,
            description=f"{stats.selfref.capitalize()} takes another action this round. If it has any recharge abilities, it may roll to refresh these abilities.",
        )
        return [feature]


class _Leap(SoldierPower):
    def __init__(self):
        super().__init__(
            name="Mighty Leap",
            source="A5E SRD Bulette",
            icon="jump-across",
            create_date=datetime(2023, 11, 23),
            require_stats=Stats.STR,
            bonus_size=Size.Large,
            require_callback=is_ground,
            require_cr=3,
            stat_threshold=14,
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dmg = stats.target_value(target=1.5, force_die=Die.d6)
        dc = stats.difficulty_class
        prone = Condition.Prone

        if stats.cr < 1:
            uses = 1
            recharge = None
        else:
            uses = None
            recharge = 5

        feature = Feature(
            name="Mighty Leap",
            action=ActionType.Action,
            replaces_multiattack=2,
            recharge=recharge,
            uses=uses,
            description=f"{stats.selfref.capitalize()} can use its action to jump up to half its speed horizontally and up to half its speed vertically \
                without provoking opportunity attacks, and can land in a space containing one or more creatures. \
                Each creature in its space when {stats.selfref} lands makes a DC {dc} Dexterity saving throw, taking {dmg.description} bludgeoning damage and being knocked {prone.caption} \
                on a failure. On a success, the creature takes half damage and is pushed 5 feet to a space of its choice.",
        )

        return [feature]


class _BreakMagic(SoldierPower):
    def __init__(self):
        super().__init__(
            name="Break Magic",
            source="A5E SRD Dread Knight",
            icon="stop-sign",
            power_level=MEDIUM_POWER,
            require_cr=8,
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Break Magic",
            action=ActionType.Action,
            replaces_multiattack=1,
            uses=1,
            description=f"{stats.selfref.capitalize()} ends all spell effects created by a 5th-level or lower spell slot on a creature, object, or point it can see within 30 feet.",
        )
        return [feature]


class _Lunge(SoldierPower):
    def __init__(self):
        super().__init__(
            name="Lunge",
            icon="knife-thrust",
            source="Foe Foundry",
            power_level=LOW_POWER,
            create_date=datetime(2025, 2, 23),
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dash = action_ref("Dash")
        feature = Feature(
            name="Lunge",
            action=ActionType.BonusAction,
            uses=1,
            description=f"{stats.selfref.capitalize()} uses {dash} and can make its next attack with advantage and an additional 5 feet of reach",
        )
        return [feature]


class _PreciseStrike(SoldierPower):
    def __init__(self):
        super().__init__(
            name="Precise Strike",
            source="Foe Foundry",
            icon="bullseye",
            power_level=MEDIUM_POWER,
            create_date=datetime(2025, 2, 23),
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Precise Strike",
            action=ActionType.Reaction,
            uses=1,
            description=f"When {stats.selfref} misses with an attack, it may turn that miss into a hit.",
        )
        return [feature]


ActionSurge: Power = _ActionSurge()
BreakMagic: Power = _BreakMagic()
Disciplined: Power = _Disciplined()
Lunge: Power = _Lunge()
MightyLeap: Power = _Leap()
PackTactics: Power = _PackTactics()
PreciseStrike: Power = _PreciseStrike()
CoordinatedStrike: Power = _CoordinatedStrike()
Phalanx: Power = _Phalanx()

SoldierPowers: list[Power] = [
    ActionSurge,
    BreakMagic,
    CoordinatedStrike,
    Disciplined,
    Lunge,
    MightyLeap,
    PackTactics,
    Phalanx,
    PreciseStrike,
]

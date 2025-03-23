from datetime import datetime
from typing import List

from foe_foundry.references import action_ref

from ...attributes import Skills, Stats
from ...creature_types import CreatureType
from ...damage import Condition
from ...die import Die
from ...features import ActionType, Feature
from ...role_types import MonsterRole
from ...size import Size
from ...statblocks import BaseStatblock
from ...utils import easy_multiple_of_five
from ..power import (
    HIGH_POWER,
    LOW_POWER,
    MEDIUM_POWER,
    Power,
    PowerType,
    PowerWithStandardScoring,
)


class Warrior(PowerWithStandardScoring):
    def __init__(
        self,
        name: str,
        source: str,
        power_level: float = MEDIUM_POWER,
        create_date: datetime | None = None,
        **score_args,
    ):
        existing_callback = score_args.pop("require_callback", None)

        def require_callback(s: BaseStatblock) -> bool:
            return s.creature_subtype == "Warrior" and (
                existing_callback(s) if existing_callback else True
            )

        super().__init__(
            name=name,
            source=source,
            power_level=power_level,
            create_date=create_date,
            power_type=PowerType.Creature,
            theme="warrior",
            score_args=dict(
                require_callback=require_callback,
                bonus_roles={
                    MonsterRole.Bruiser,
                    MonsterRole.Defender,
                    MonsterRole.Soldier,
                },
                bonus_skills=Skills.Athletics,
            )
            | score_args,
        )


class _PackTactics(Warrior):
    def __init__(self):
        super().__init__(
            name="Pack Tactics",
            source="SRD5.1 Wolf",
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


class _Disciplined(Warrior):
    def __init__(self):
        super().__init__(
            name="Disciplined", source="Foe Foundry", require_roles=MonsterRole.Soldier
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Disciplined",
            action=ActionType.Reaction,
            description=f"If {stats.selfref} misses an attack or fails a saving throw while another friendly creature is within 10 feet, it may use its reaction to re-roll the attack or saving throw.",
        )
        return [feature]


class _ActionSurge(Warrior):
    def __init__(self):
        super().__init__(
            name="Action Surge",
            source="SRD5.1 Action Surge",
            power_level=HIGH_POWER,
            bonus_roles={MonsterRole.Soldier},
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Action Surge",
            uses=1,
            action=ActionType.BonusAction,
            description=f"{stats.selfref.capitalize()} takes another action this round. If it has any recharge abilities, it may roll to refresh these abilities.",
        )
        return [feature]


class _Leap(Warrior):
    def __init__(self):
        def is_ground(c: BaseStatblock) -> bool:
            return (c.speed.fly or 0) == 0

        super().__init__(
            name="Mighty Leap",
            source="A5E SRD Bulette",
            create_date=datetime(2023, 11, 23),
            require_stats=Stats.STR,
            bonus_size=Size.Large,
            require_callback=is_ground,
            stat_threshold=14,
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dmg = stats.target_value(1.5, force_die=Die.d6)
        dc = stats.difficulty_class
        prone = Condition.Prone

        feature = Feature(
            name="Mighty Leap",
            action=ActionType.Action,
            replaces_multiattack=2,
            recharge=5,
            description=f"{stats.selfref.capitalize()} can use its action to jump up to half its speed horizontally and up to half its speed vertically \
                without provoking opportunity attacks, and can land in a space containing one or more creatures. \
                Each creature in its space when {stats.selfref} lands makes a DC {dc} Dexterity saving throw, taking {dmg.description} bludgeoning damage and being knocked {prone.caption} \
                on a failure. On a success, the creature takes half damage and is pushed 5 feet to a space of its choice.",
        )

        return [feature]


class _BreakMagic(Warrior):
    def __init__(self):
        super().__init__(
            name="Break Magic",
            source="A5E SRD Dread Knight",
            power_level=MEDIUM_POWER,
            require_cr=8,
            bonus_roles={MonsterRole.Bruiser, MonsterRole.Soldier},
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


class _Lunge(Warrior):
    def __init__(self):
        super().__init__(
            name="Lunge",
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


class _CommandTheTroops(Warrior):
    def __init__(self):
        super().__init__(
            name="Command the Troops",
            source="Foe Foundry",
            power_level=MEDIUM_POWER,
            create_date=datetime(2025, 2, 23),
            require_cr=3,
            bonus_roles={MonsterRole.Leader},
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Command the Troops",
            action=ActionType.Action,
            replaces_multiattack=1,
            description=f"{stats.selfref.capitalize()} commands a willing creature within 30 feet to use its reaction and make an attack at advantage",
        )

        return [feature]


class _RallyTheTroops(Warrior):
    def __init__(self):
        super().__init__(
            name="Rally the Troops",
            source="Foe Foundry",
            power_level=MEDIUM_POWER,
            create_date=datetime(2025, 2, 23),
            require_cr=3,
            bonus_roles={MonsterRole.Leader},
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        hp = easy_multiple_of_five(stats.target_value(0.5).average, min_val=5)

        feature = Feature(
            name="Rally the Troops",
            action=ActionType.Action,
            replaces_multiattack=1,
            recharge=5,
            description=f"{stats.selfref.capitalize()} rallies all friendly creatures within 60 feet, granting them {hp} temporary hit points.",
        )

        return [feature]


class _PreciseStrike(Warrior):
    def __init__(self):
        super().__init__(
            name="Precise Strike",
            source="Foe Foundry",
            power_level=MEDIUM_POWER,
            create_date=datetime(2025, 2, 23),
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Precise Strike",
            action=ActionType.Reaction,
            uses=1,
            description=f"When {stats.selfref.capitalize()} misses with an attack, it may turn that miss into a hit.",
        )
        return [feature]


ActionSurge: Power = _ActionSurge()
BreakMagic: Power = _BreakMagic()
CommandTheTroops: Power = _CommandTheTroops()
Disciplined: Power = _Disciplined()
Lunge: Power = _Lunge()
MightyLeap: Power = _Leap()
PackTactics: Power = _PackTactics()
PreciseStrike: Power = _PreciseStrike()
RallyTheTroops: Power = _RallyTheTroops()

WarriorPowers: List[Power] = [
    ActionSurge,
    BreakMagic,
    CommandTheTroops,
    Disciplined,
    Lunge,
    MightyLeap,
    PackTactics,
    PreciseStrike,
    RallyTheTroops,
]

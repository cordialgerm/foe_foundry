from datetime import datetime
from typing import List

from foe_foundry.utils import easy_multiple_of_five

from ...creature_types import CreatureType
from ...damage import Condition
from ...features import ActionType, Feature
from ...power_types import PowerType
from ...statblocks import BaseStatblock
from ..power import (
    LOW_POWER,
    MEDIUM_POWER,
    Power,
    PowerCategory,
    PowerWithStandardScoring,
)


class ZombiePower(PowerWithStandardScoring):
    def __init__(
        self,
        *,
        name: str,
        source: str,
        icon: str,
        power_level: float = MEDIUM_POWER,
        power_types: List[PowerType],
        create_date: datetime | None = None,
        **score_args,
    ):
        def require_callback(s: BaseStatblock) -> bool:
            existing_callback = score_args.get("require_callback")
            return s.creature_subtype == "Zombie" and (
                existing_callback(s) if existing_callback else True
            )

        super().__init__(
            name=name,
            source=source,
            theme="zombie",
            reference_statblock="Zombie",
            icon=icon,
            power_level=power_level,
            power_category=PowerCategory.Creature,
            power_types=power_types,
            create_date=create_date,
            score_args=dict(
                require_callback=require_callback,
                require_types=[CreatureType.Undead],
            )
            | score_args,
        )


class _RottenFlesh(ZombiePower):
    def __init__(self):
        super().__init__(
            name="Rotten Flesh",
            source="Foe Foundry",
            icon="shambling-zombie",
            power_level=LOW_POWER,
            power_types=[PowerType.Defense],
            create_date=datetime(2025, 2, 20),
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Rotten Flesh",
            action=ActionType.Reaction,
            uses=1,
            description=f"{stats.selfref.capitalize()} ignores the first source of bludgeoning, piercing, or slashing damage it receives.",
        )
        return [feature]


class _PutridStench(ZombiePower):
    def __init__(self):
        super().__init__(
            name="Putrid Stench",
            source="Foe Foundry",
            icon="carrion",
            power_level=MEDIUM_POWER,
            power_types=[PowerType.AreaOfEffect, PowerType.Attack, PowerType.Debuff],
            create_date=datetime(2025, 2, 20),
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        damage = stats.target_value(target=1.0)
        dc = stats.difficulty_class_easy
        poisoned = Condition.Poisoned

        feature = Feature(
            name="Putrid Stench",
            action=ActionType.Reaction,
            uses=1,
            description=f"{stats.selfref.capitalize()} releases a putrid stench when it takes damage. Each creature within 5 feet must make a DC {dc} Constitution save or take {damage.description} poison damage and be {poisoned.caption} until the end of their next turn.",
        )
        return [feature]


class _SeveredLimb(ZombiePower):
    def __init__(self):
        super().__init__(
            name="Severed Limb",
            icon="severed-hand",
            source="Foe Foundry",
            power_level=LOW_POWER,
            power_types=[PowerType.Debuff],
            create_date=datetime(2025, 2, 20),
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class
        grappled = Condition.Grappled
        restrained = Condition.Restrained
        feature = Feature(
            name="Severed Limb",
            action=ActionType.Reaction,
            uses=stats.attributes.proficiency // 2,
            description=f"When {stats.selfref} takes damage, one of its decaying limbs sloughs off and attempts to grapple the source of the damage if it is within 5 feet of {stats.selfref}. The target must make a DC {dc} Strength save or be {grappled.caption} (escape DC {dc}) and {restrained.caption} by the limb.",
        )
        return [feature]


class _WontStopComing(ZombiePower):
    def __init__(self):
        super().__init__(
            name="Won't Stop Coming",
            icon="half-body-crawling",
            source="Foe Foundry",
            power_level=LOW_POWER,
            power_types=[PowerType.Buff],
            create_date=datetime(2025, 7, 13),
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        hp = easy_multiple_of_five(stats.hp.average / 2, min_val=5)
        feature = Feature(
            name="Won't Stop Coming",
            uses=1,
            action=ActionType.Reaction,
            description=f"When {stats.selfref} is reduced to 0 hit points, it instead resets its hitpoints to {hp} and may shamble up to half its movement speed towards the nearest creature. \
                This ability cannot be used if the damage is radiant or from a critical hit.",
        )
        return [feature]


PutridStench: Power = _PutridStench()
RottenFlesh: Power = _RottenFlesh()
SeveredLimb: Power = _SeveredLimb()
WontStopComing: Power = _WontStopComing()

ZombiePowers: list[Power] = [PutridStench, RottenFlesh, SeveredLimb, WontStopComing]

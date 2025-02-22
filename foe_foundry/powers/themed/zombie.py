from datetime import datetime
from typing import List

from ...creature_types import CreatureType
from ...features import ActionType, Feature
from ...statblocks import BaseStatblock
from ..power import LOW_POWER, MEDIUM_POWER, Power, PowerType, PowerWithStandardScoring


class ZombiePower(PowerWithStandardScoring):
    def __init__(
        self,
        name: str,
        source: str,
        power_level: float = MEDIUM_POWER,
        create_date: datetime | None = None,
        **score_args,
    ):
        super().__init__(
            name=name,
            source=source,
            theme="zombie",
            power_level=power_level,
            power_type=PowerType.Creature,
            create_date=create_date,
            score_args=dict(
                require_types=[CreatureType.Undead],
            )
            | score_args,
        )


class _RottenFlesh(ZombiePower):
    def __init__(self):
        super().__init__(
            name="Rotten Flesh",
            source="Foe Foundry",
            power_level=LOW_POWER,
            create_date=datetime(2025, 2, 20),
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Rotten Flesh",
            action=ActionType.Reaction,
            uses=1,
            description=f"{stats.selfref.title()} ignores the first source of bludgeoning, piercing, or slashing damage it receives.",
        )
        return [feature]


class _PutridStench(ZombiePower):
    def __init__(self):
        super().__init__(
            name="Putrid Stench",
            source="Foe Foundry",
            power_level=MEDIUM_POWER,
            create_date=datetime(2025, 2, 20),
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        damage = stats.target_value(1.0)
        dc = stats.difficulty_class_easy

        feature = Feature(
            name="Putrid Stench",
            action=ActionType.Reaction,
            uses=1,
            description=f"{stats.selfref.title()} releases a putrid stench when it takes damage. Each creature within 5 feet must make a DC {dc} Constitution save or take {damage.description} poison damage and be **Poisoned** until the end of their next turn.",
        )
        return [feature]


class _SeveredLimb(ZombiePower):
    def __init__(self):
        super().__init__(
            name="Severed Limb",
            source="Foe Foundry",
            power_level=LOW_POWER,
            create_date=datetime(2025, 2, 20),
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class
        feature = Feature(
            name="Severed Limb",
            action=ActionType.Reaction,
            uses=1,
            description=f"When {stats.selfref} takes damage, one of its decaying limbs sloughs off and attempts to grapple the source of the damage if it is within 5 feet of {stats.selfref}. The target must make a DC {dc} Strength save or be **Grappled** (escape DC {dc}) and **Restrained** by the limb.",
        )
        return [feature]


PutridStench: Power = _PutridStench()
RottenFlesh: Power = _RottenFlesh()
SeveredLimb: Power = _SeveredLimb()

ZombiePowers: list[Power] = [PutridStench, RottenFlesh, SeveredLimb]

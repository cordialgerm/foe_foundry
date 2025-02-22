from datetime import datetime
from typing import List

from ...creature_types import CreatureType
from ...features import ActionType, Feature
from ...role_types import MonsterRole
from ...statblocks import BaseStatblock
from ..power import (
    HIGH_POWER,
    MEDIUM_POWER,
    PowerType,
    PowerWithStandardScoring,
)


class SkeletalPower(PowerWithStandardScoring):
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
            theme="skeletal",
            power_level=power_level,
            power_type=PowerType.Creature,
            create_date=create_date,
            score_args=dict(
                require_types=[CreatureType.Undead],
            )
            | score_args,
        )


def is_minion(stats: BaseStatblock) -> bool:
    return MonsterRole.Leader not in stats.additional_roles and stats.cr <= 6


class _SkeletalReconstruction(SkeletalPower):
    def __init__(self):
        super().__init__(
            name="Skeletal Reconstruction",
            power_level=HIGH_POWER,
            source="Foe Foundry",
            create_date=datetime(2025, 2, 19),
            require_callback=is_minion,
            bonus_roles=MonsterRole.Defender,
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Skeletal Reconstruction",
            action=ActionType.Feature,
            description=f"On initiative count 0, the cursed bones of three destroyed {stats.name} within 30 feet combine and magically re-animate into a new {stats.name} that acts next in initiative.",
        )

        return [feature]


class _BoneShards(SkeletalPower):
    def __init__(self):
        super().__init__(
            name="Bone Shards",
            power_level=MEDIUM_POWER,
            source="Foe Foundry",
            create_date=datetime(2025, 2, 19),
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class_easy
        damage = stats.target_value(0.75)

        feature = Feature(
            name="Bone Shards",
            action=ActionType.Reaction,
            uses=1,
            description=f"When hit by a melee attack, the skeletal creature explodes in a shower of sharp fragments. Each creature within 5 feet of it must make a DC {dc} Dexterity saving throw, taking {damage} piercing damage on a failed save, or half as much damage on a successful one.",
        )

        return [feature]


class _LoathsomeRattle(SkeletalPower):
    def __init__(self):
        super().__init__(
            name="Loathsome Rattle",
            power_level=MEDIUM_POWER,
            source="Foe Foundry",
            create_date=datetime(2025, 2, 19),
            bonus_roles=[MonsterRole.Controller, MonsterRole.Skirmisher],
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class_easy

        feature = Feature(
            name="Loathsome Rattle",
            action=ActionType.BonusAction,
            uses=1,
            description=f"{stats.selfref.title()} rattles its bones in a cacophony of sound, causing all who hear it to feel a chill of fear. Each non-undead within 30 feet must make a DC {dc} Wisdom saving throw or be **Frightened** until the end of the skeletal creature's next turn.",
        )

        return [feature]


class _BoneSpear(SkeletalPower):
    def __init__(self):
        super().__init__(
            name="Bone Spear",
            power_level=MEDIUM_POWER,
            source="Foe Foundry",
            create_date=datetime(2025, 2, 19),
            bonus_roles=[MonsterRole.Artillery, MonsterRole.Controller],
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        damage = stats.target_value(0.7 * min(stats.multiattack, 2))

        feature = Feature(
            name="Bone Harpoon",
            action=ActionType.Action,
            replaces_multiattack=2,
            description=f"{stats.selfref.title()} hurls a bone spear at a target within 60 feet. The target must make a DC {stats.difficulty_class_easy} Dexterity saving throw. On a failure, the target takes {damage} piercing damage and is pushed up to 10 feet away.",
        )

        return [feature]


class _BoneStorm(SkeletalPower):
    def __init__(self):
        super().__init__(
            name="Bone Storm",
            power_level=MEDIUM_POWER,
            source="Foe Foundry",
            create_date=datetime(2025, 2, 19),
            bonus_roles=[MonsterRole.Artillery, MonsterRole.Controller],
            require_cr=4,
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        damage = stats.target_value(1.2 * min(stats.multiattack, 2))

        feature = Feature(
            name="Bone Storm",
            action=ActionType.Action,
            replaces_multiattack=2,
            recharge=5,
            description=f"{stats.selfref.title()} creates a storm of razor-sharp bone shards in a 15-foot cone. Each creature in the area must make a DC {stats.difficulty_class_easy} Dexterity saving throw, taking {damage} piercing damage on a failed save, or half as much damage on a successful one.",
        )

        return [feature]


class _BoneWall(SkeletalPower):
    def __init__(self):
        super().__init__(
            name="Bone Wall",
            power_level=MEDIUM_POWER,
            source="Foe Foundry",
            create_date=datetime(2025, 2, 19),
            bonus_roles=[MonsterRole.Defender, MonsterRole.Controller],
            require_cr=4,
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        damage = stats.target_value(0.5 * min(stats.multiattack, 2))

        feature = Feature(
            name="Bone Wall",
            action=ActionType.Action,
            replaces_multiattack=2,
            recharge=5,
            description=f"{stats.selfref.title()} creates a wall of spike bone growths in a 20 foot line within 60 feet. Each creature in its area must make a DC {stats.difficulty_class_easy} Dexterity saving throw, taking {damage} piercing damage on a failed save, or half as much damage on a successful one. The wall counts as difficult terrain and a creature that enters its space or ends its turn there takes {damage} piercing damage.",
        )

        return [feature]


SkeletalReconstruction: SkeletalPower = _SkeletalReconstruction()
BoneShards: SkeletalPower = _BoneShards()
LoathsomeRattle: SkeletalPower = _LoathsomeRattle()
BoneSpear: SkeletalPower = _BoneSpear()
BoneStorm: SkeletalPower = _BoneStorm()
BoneWall: SkeletalPower = _BoneWall()

SkeletalPowers: List[SkeletalPower] = [
    BoneShards,
    BoneSpear,
    BoneStorm,
    BoneWall,
    LoathsomeRattle,
    SkeletalReconstruction,
]

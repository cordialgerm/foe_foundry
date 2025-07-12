from datetime import datetime
from typing import List

from ...creature_types import CreatureType
from ...damage import Condition
from ...features import ActionType, Feature
from ...role_types import MonsterRole
from ...statblocks import BaseStatblock
from ..power import (
    HIGH_POWER,
    MEDIUM_POWER,
    Power,
    PowerCategory,
    PowerWithStandardScoring,
)


class SkeletalPower(PowerWithStandardScoring):
    def __init__(
        self,
        name: str,
        source: str,
        icon: str,
        power_level: float = MEDIUM_POWER,
        create_date: datetime | None = None,
        **score_args,
    ):
        existing_callback = score_args.pop("require_callback", None)

        def require_callback(s: BaseStatblock) -> bool:
            return s.creature_subtype == "Skeletal" and (
                existing_callback(s) if existing_callback else True
            )

        super().__init__(
            name=name,
            source=source,
            theme="skeleton",
            icon=icon,
            reference_statblock="Skeleton",
            power_level=power_level,
            power_category=PowerCategory.Creature,
            create_date=create_date,
            score_args=dict(
                require_callback=require_callback,
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
            icon="raise-skeleton",
            source="Foe Foundry",
            create_date=datetime(2025, 2, 19),
            require_callback=is_minion,
            bonus_roles=MonsterRole.Defender,
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
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
            icon="edge-crack",
            source="Foe Foundry",
            create_date=datetime(2025, 2, 19),
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class_easy
        damage = stats.target_value(target=0.75)

        feature = Feature(
            name="Bone Shards",
            action=ActionType.Reaction,
            uses=1,
            description=f"When hit by a melee attack, the skeletal creature explodes in a shower of sharp fragments. Each creature within 5 feet of it must make a DC {dc} Dexterity saving throw, taking {damage.description} piercing damage on a failed save, or half as much damage on a successful one.",
        )

        return [feature]


class _LoathsomeRattle(SkeletalPower):
    def __init__(self):
        super().__init__(
            name="Loathsome Rattle",
            power_level=MEDIUM_POWER,
            source="Foe Foundry",
            icon="rattlesnake",
            create_date=datetime(2025, 2, 19),
            bonus_roles=[MonsterRole.Controller, MonsterRole.Skirmisher],
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class_easy
        frightened = Condition.Frightened

        feature = Feature(
            name="Loathsome Rattle",
            action=ActionType.BonusAction,
            uses=1,
            description=f"{stats.selfref.capitalize()} rattles its bones in a cacophony of sound, causing all who hear it to feel a chill of fear. Each non-undead within 30 feet must make a DC {dc} Wisdom saving throw or be {frightened.caption} until the end of the skeletal creature's next turn.",
        )

        return [feature]


class _BoneSpear(SkeletalPower):
    def __init__(self):
        super().__init__(
            name="Bone Spear",
            power_level=MEDIUM_POWER,
            source="Foe Foundry",
            icon="spine-arrow",
            create_date=datetime(2025, 2, 19),
            bonus_roles=[MonsterRole.Artillery, MonsterRole.Controller],
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        damage = stats.target_value(target=0.7 * min(stats.multiattack, 2))

        feature = Feature(
            name="Bone Harpoon",
            action=ActionType.Action,
            replaces_multiattack=2,
            description=f"{stats.selfref.capitalize()} hurls a bone spear at a target within 60 feet. The target must make a DC {stats.difficulty_class_easy} Dexterity saving throw. On a failure, the target takes {damage.description} piercing damage and is pushed up to 10 feet away.",
        )

        return [feature]


class _BoneStorm(SkeletalPower):
    def __init__(self):
        super().__init__(
            name="Bone Storm",
            power_level=MEDIUM_POWER,
            source="Foe Foundry",
            icon="striking-splinter",
            create_date=datetime(2025, 2, 19),
            bonus_roles=[MonsterRole.Artillery, MonsterRole.Controller],
            require_cr=4,
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        damage = stats.target_value(target=1.2 * min(stats.multiattack, 2))

        if stats.cr < 1:
            recharge = None
            uses = 1
        else:
            recharge = 5
            uses = None

        feature = Feature(
            name="Bone Storm",
            action=ActionType.Action,
            replaces_multiattack=2,
            recharge=recharge,
            uses=uses,
            description=f"{stats.selfref.capitalize()} creates a storm of razor-sharp bone shards in a 15-foot cone. Each creature in the area must make a DC {stats.difficulty_class_easy} Dexterity saving throw, taking {damage.description} piercing damage on a failed save, or half as much damage on a successful one.",
        )

        return [feature]


class _BoneWall(SkeletalPower):
    def __init__(self):
        super().__init__(
            name="Bone Wall",
            power_level=MEDIUM_POWER,
            source="Foe Foundry",
            icon="stakes-fence",
            create_date=datetime(2025, 2, 19),
            bonus_roles=[MonsterRole.Defender, MonsterRole.Controller],
            require_cr=4,
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        damage = stats.target_value(target=0.5 * min(stats.multiattack, 2))

        if stats.cr < 1:
            uses = 1
            recharge = None
        else:
            uses = None
            recharge = 5

        feature = Feature(
            name="Bone Wall",
            action=ActionType.Action,
            replaces_multiattack=2,
            recharge=recharge,
            uses=uses,
            description=f"{stats.selfref.capitalize()} creates a wall of spike bone growths in a 20 foot line within 60 feet. Each creature in its area must make a DC {stats.difficulty_class_easy} Dexterity saving throw, taking {damage.description} piercing damage on a failed save, or half as much damage on a successful one. The wall counts as difficult terrain and a creature that enters its space or ends its turn there takes {damage} piercing damage.",
        )

        return [feature]


SkeletalReconstruction: SkeletalPower = _SkeletalReconstruction()
BoneShards: SkeletalPower = _BoneShards()
LoathsomeRattle: SkeletalPower = _LoathsomeRattle()
BoneSpear: SkeletalPower = _BoneSpear()
BoneStorm: SkeletalPower = _BoneStorm()
BoneWall: SkeletalPower = _BoneWall()

SkeletalPowers: List[Power] = [
    BoneShards,
    BoneSpear,
    BoneStorm,
    BoneWall,
    LoathsomeRattle,
    SkeletalReconstruction,
]

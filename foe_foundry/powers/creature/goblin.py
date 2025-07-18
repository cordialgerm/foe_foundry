from datetime import datetime
from typing import List

from ...creature_types import CreatureType
from ...damage import Condition, conditions
from ...features import ActionType, Feature
from ...power_types import PowerType
from ...role_types import MonsterRole
from ...statblocks import BaseStatblock
from ..power import (
    LOW_POWER,
    MEDIUM_POWER,
    Power,
    PowerCategory,
    PowerWithStandardScoring,
)


def is_goblin(s: BaseStatblock) -> bool:
    return s.creature_class == "Goblin"


class GoblinPower(PowerWithStandardScoring):
    def __init__(
        self,
        name: str,
        source: str,
        icon: str,
        power_level: float = MEDIUM_POWER,
        create_date: datetime | None = datetime(2025, 3, 22),
        power_types: List[PowerType] | None = None,
        **score_args,
    ):
        super().__init__(
            name=name,
            source=source,
            theme="goblin",
            icon=icon,
            reference_statblock="Goblin",
            power_level=power_level,
            power_category=PowerCategory.Creature,
            create_date=create_date,
            power_types=power_types,
            score_args=dict(
                require_callback=is_goblin,
                require_types=[CreatureType.Humanoid],
            )
            | score_args,
        )


class _FlingFilth(GoblinPower):
    def __init__(self):
        super().__init__(
            name="Fling Filth",
            source="Foe Foundry",
            icon="throwing-ball",
            power_level=LOW_POWER,
            require_max_cr=1,
            power_types=[PowerType.Attack, PowerType.Debuff],
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class_easy
        blinded = Condition.Blinded

        feature = Feature(
            name="Fling Filth",
            action=ActionType.Action,
            replaces_multiattack=1,
            description=f"{stats.selfref.capitalize()} flings filth at a creature within 10 feet. \
            The target must make a DC {dc} Dexterity saving throw or be {blinded.caption} until the end of its next turn.",
        )

        return [feature]


class _CacklingDetonation(GoblinPower):
    def __init__(self):
        def require_callback(s: BaseStatblock) -> bool:
            return (
                is_goblin(s)
                and MonsterRole.Leader not in s.additional_roles
                and s.cr < 1
            )

        super().__init__(
            name="Cackling Detonation",
            source="Foe Foundry",
            icon="dynamite",
            power_level=LOW_POWER,
            require_max_cr=0.5,
            require_callback=require_callback,
            power_types=[PowerType.AreaOfEffect, PowerType.Attack],
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class_easy
        dmg = stats.target_value(dpr_proportion=1.4)
        bloodied = Condition.Bloodied
        feature = Feature(
            name="Cackling Detonation",
            action=ActionType.Action,
            description=f"If {stats.selfref} is {bloodied.caption} and there is at least one higher-CR ally within 60 feet, then {stats.selfref} cackles and detonates a highly volatile explosive concoction, instantly killing it. \
                Each other creature within 10 feet must make a DC {dc} Dexterity saving throw, taking {dmg.description} fire damage on a failed save and half damage on success.",
        )
        return [feature]


class _CackleHex(GoblinPower):
    def __init__(self):
        super().__init__(
            name="Cacklehex",
            source="Foe Foundry",
            icon="imp-laugh",
            require_cr=1,
            require_spellcasting=True,
            power_types=[PowerType.Debuff, PowerType.Attack],
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class
        prone = Condition.Prone
        cursed = conditions.Cursed().caption
        dmg = stats.target_value(dpr_proportion=0.7)

        feature = Feature(
            name="Cacklehex",
            action=ActionType.Action,
            replaces_multiattack=2,
            recharge=5,
            description=f"{stats.selfref.capitalize()} curses a creature it can see within 60 feet with a Cacklehex. \
                The target must make a DC {dc} Wisdom saving throw. On a failure, it takes {dmg.description} psychic damage and is {cursed} (save ends at end of turn). \
                While cursed, it falls {prone.caption} and it cannot stand up.",
        )

        return [feature]


class _BloodCurse(GoblinPower):
    def __init__(self):
        super().__init__(
            name="Blood Curse",
            source="Foe Foundry",
            icon="blood",
            power_level=LOW_POWER,
            require_cr=1,
            require_spellcasting=True,
            power_types=[PowerType.Debuff],
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        dmg = stats.target_value(dpr_proportion=0.5)

        feature = Feature(
            name="Blood Curse",
            action=ActionType.BonusAction,
            uses=1,
            description=f"{stats.selfref.capitalize()} takes {dmg.description} necrotic damage as it ceremonially cuts itself and curses the blood of a creature it can see within 60 feet. \
                After this, whenever {stats.selfref} takes damage, the cursed creature takes half that damage (rounded down) as psychic damage.",
        )

        return [feature]


FlingFilth: Power = _FlingFilth()
CacklingDetonation: Power = _CacklingDetonation()
CackleHex: Power = _CackleHex()
BloodCurse: Power = _BloodCurse()

GoblinPowers: list[Power] = [
    FlingFilth,
    CacklingDetonation,
    CackleHex,
    BloodCurse,
]

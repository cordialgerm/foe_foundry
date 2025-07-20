from datetime import datetime
from math import ceil
from typing import List

from ...attributes import AbilityScore, Skills
from ...damage import AttackType, Condition, conditions
from ...die import Die
from ...features import ActionType, Feature
from ...power_types import PowerType
from ...role_types import MonsterRole
from ...statblocks import BaseStatblock
from ..power import (
    HIGH_POWER,
    LOW_POWER,
    MEDIUM_POWER,
    Power,
    PowerCategory,
    PowerWithStandardScoring,
)


class ArtilleryPower(PowerWithStandardScoring):
    def __init__(
        self,
        name: str,
        source: str,
        icon: str,
        create_date: datetime | None = None,
        power_level: float = MEDIUM_POWER,
        reference_statblock: str = "Scout",
        power_types: List[PowerType] | None = None,
        **score_args,
    ):
        standard_score_args = (
            dict(
                require_roles=MonsterRole.Artillery,
                require_attack_types=AttackType.AllRanged(),
                bonus_stats=[AbilityScore.DEX, AbilityScore.INT],
                bonus_skills=Skills.Perception,
            )
            | score_args
        )
        super().__init__(
            name=name,
            power_category=PowerCategory.Role,
            power_level=power_level,
            source=source,
            create_date=create_date,
            icon=icon,
            theme="Artillery",
            reference_statblock=reference_statblock,
            power_types=power_types,
            score_args=standard_score_args,
        )


class _FocusShot(ArtilleryPower):
    def __init__(self):
        super().__init__(
            name="Focus Shot",
            source="A5E SRD Focus Shot",
            icon="archery-target",
            create_date=datetime(2023, 11, 23),
            power_level=HIGH_POWER,
            require_attack_types=AttackType.RangedWeapon,
            power_types=[PowerType.Attack, PowerType.Debuff],
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        bleeding = conditions.Bleeding(
            damage=stats.target_value(target=0.25, force_die=Die.d6)
        )
        blinded = Condition.Blinded
        prone = Condition.Prone
        dc = stats.difficulty_class
        feature = Feature(
            name="Focus Shot",
            action=ActionType.BonusAction,
            recharge=4,
            description=f"If {stats.roleref} has not moved this turn, it gains advantage on the next attack roll it makes this turn. Its speed becomes 0 until the start of its next turn. \
                If the attack hits, {stats.roleref} can choose one of the following options: \
                <ul>\
                    <li>**Aim for the Eyes**: the target must make a DC {dc} Dexterity saving throw or be {blinded.caption} for 1 minute (save ends at end of turn)</li> \
                    <li>**Bring it Down**: the target must make a DC {dc} Strength saving throw or be knocked {prone.caption}</li> \
                    <li>**Vein Slice**: the target must make a DC {dc} Constitution saving throw or gain {bleeding.caption}. {bleeding.description_3rd} \
                </ul>",
        )
        return [feature]


class _TwinSpell(ArtilleryPower):
    def __init__(self):
        super().__init__(
            name="Twin Spell",
            source="5.1SRD Twin Spell",
            icon="double-shot",
            create_date=datetime(2023, 11, 23),
            power_level=HIGH_POWER,
            require_attack_types=AttackType.RangedSpell,
            power_types=[PowerType.Attack],
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Twin Spell",
            action=ActionType.BonusAction,
            recharge=4,
            description=f"Immediately after hitting with a spell attack, {stats.roleref} can repeat the attack against a different target in range.",
        )
        return [feature]


class _QuickDraw(ArtilleryPower):
    def __init__(self):
        super().__init__(
            name="Quick Draw",
            source="Foe Foundry",
            icon="fast-arrow",
            power_level=LOW_POWER,
            power_types=[PowerType.Attack],
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        uses = ceil(stats.cr / 5)
        feature = Feature(
            name="Quick Draw",
            action=ActionType.Reaction,
            description=f"On initiative count 20, {stats.selfref} may make one ranged attack",
            uses=uses,
        )
        return [feature]


class _SuppressingFire(ArtilleryPower):
    def __init__(self):
        super().__init__(
            name="Suppressing Fire",
            icon="oppression",
            source="Foe Foundry",
            power_types=[PowerType.Attack, PowerType.Debuff],
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Suppressing Fire",
            action=ActionType.Feature,
            description="On a hit, the target's speed is reduced by half until the end of its next turn",
            hidden=True,
            modifies_attack=True,
        )
        return [feature]


def not_gaze(stats: BaseStatblock) -> bool:
    return "gaze" not in stats.attack.name.lower()


class _IndirectFire(ArtilleryPower):
    def __init__(self):
        super().__init__(
            name="Indirect Fire",
            source="Foe Foundry",
            icon="arcing-bolt",
            power_level=LOW_POWER,
            require_callback=not_gaze,
            power_types=[PowerType.Utility],
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Indirect Fire",
            action=ActionType.Feature,
            description=f"{stats.roleref.capitalize()} can perform its ranged attacks indirectly, such as by arcing or curving shots. It ignores half and three-quarters cover. \
                These attacks are often unexpected. If it makes a ranged attack against a creature with half or three-quarters cover that is not yet aware of this ability, the attack is made at advantage. \
                Any creature that can see the attack occuring is then aware of this ability.",
        )
        return [feature]


class _Overwatch(ArtilleryPower):
    def __init__(self):
        super().__init__(
            name="Overwatch",
            source="Foe Foundry",
            icon="watchtower",
            power_level=LOW_POWER,
            power_types=[PowerType.Attack],
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        range = stats.attack.range or 60

        if stats.cr < 1:
            recharge = None
            uses = 1
        else:
            recharge = 4
            uses = None

        feature = Feature(
            name="Overwatch",
            action=ActionType.Reaction,
            recharge=recharge,
            uses=uses,
            description=f"When a hostile creature within {range} feet of {stats.roleref} moves and {stats.roleref} can see that movement, it can make a ranged attack against the target.",
        )
        return [feature]


FocusShot: Power = _FocusShot()
IndirectFire: Power = _IndirectFire()
Overwatch: Power = _Overwatch()
QuickDraw: Power = _QuickDraw()
SuppresingFire: Power = _SuppressingFire()
TwinSpell: Power = _TwinSpell()


ArtilleryPowers: List[Power] = [
    FocusShot,
    IndirectFire,
    Overwatch,
    QuickDraw,
    SuppresingFire,
]

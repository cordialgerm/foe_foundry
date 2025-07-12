from datetime import datetime
from typing import List

from foe_foundry.references import action_ref

from ...attributes import Skills, Stats
from ...creature_types import CreatureType
from ...damage import AttackType, Condition
from ...die import Die
from ...features import ActionType, Feature
from ...role_types import MonsterRole
from ...statblocks import BaseStatblock
from ..power import (
    HIGH_POWER,
    LOW_POWER,
    MEDIUM_POWER,
    RIBBON_POWER,
    Power,
    PowerCategory,
    PowerWithStandardScoring,
)


def no_unique_movement(stats: BaseStatblock) -> bool:
    return not stats.has_unique_movement_manipulation


def not_caster(stats: BaseStatblock) -> bool:
    return stats.caster_type is None


class SneakyPower(PowerWithStandardScoring):
    def __init__(
        self,
        name: str,
        source: str,
        icon: str,
        power_level: float = MEDIUM_POWER,
        create_date: datetime | None = None,
        **score_args,
    ):
        super().__init__(
            name=name,
            source=source,
            icon=icon,
            theme="sneaky",
            reference_statblock="Spy",
            power_level=power_level,
            power_type=PowerCategory.Theme,
            create_date=create_date,
            score_args=dict(
                require_roles=[
                    MonsterRole.Ambusher,
                    MonsterRole.Skirmisher,
                ],
                require_stats=Stats.DEX,
                bonus_skills=Skills.Stealth,
                stat_threshold=14,
            )
            | score_args,
        )


class _SneakyStrike(SneakyPower):
    def __init__(self):
        super().__init__(
            name="Sneaky Strike",
            source="Foe Foundry",
            icon="backstab",
            power_level=HIGH_POWER,
            require_attack_types=AttackType.AllWeapon(),
        )

    def modify_stats_inner(self, stats: BaseStatblock) -> BaseStatblock:
        stats = super().modify_stats_inner(stats)
        # note: reduce overall damage because we're going to boost damage substantially if it's made with advantage
        stats = stats.copy(damage_modifier=0.9 * stats.damage_modifier)
        return stats

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        dmg = stats.target_value(target=0.5, force_die=Die.d6)
        damage_type = stats.attack.damage.damage_type

        feature = Feature(
            name="Sneaky Strike",
            description=f"If the attack was made with advantage, it deals an additional {dmg.description} {damage_type} damage.",
            action=ActionType.Feature,
            modifies_attack=True,
            hidden=True,
        )

        return [feature]


class _FalseAppearance(SneakyPower):
    def __init__(self):
        super().__init__(
            name="False Appearance",
            source="SRD5.1 Animated Armor",
            icon="domino-mask",
            power_level=RIBBON_POWER,
            require_types=[
                CreatureType.Plant,
                CreatureType.Construct,
                CreatureType.Ooze,
            ],
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="False Appearance",
            action=ActionType.Feature,
            description=f"As long as {stats.selfref} remains motionless it is indistinguishable from its surrounding terrain.",
        )
        return [feature]


class _Vanish(SneakyPower):
    def __init__(self):
        super().__init__(
            name="Vanish",
            icon="invisible",
            source="SRD5.1 Ranger",
            require_callback=no_unique_movement,
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        hide = action_ref("hide")
        feature = Feature(
            name="Vanish",
            description=f"{stats.selfref.capitalize()} can {hide} as a bonus action even if only lightly obscured.",
            action=ActionType.BonusAction,
        )
        return [feature]

    def modify_stats_inner(self, stats: BaseStatblock) -> BaseStatblock:
        new_attrs = stats.attributes.grant_proficiency_or_expertise(Skills.Stealth)
        stats = stats.copy(attributes=new_attrs, has_unique_movement_manipulation=True)
        return stats


class _CheapShot(SneakyPower):
    def __init__(self):
        super().__init__(
            name="Cheap Shot",
            source="Foe Foundry",
            icon="tripwire",
            require_attack_types=AttackType.AllMelee(),
            power_level=LOW_POWER,
            require_callback=not_caster,
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class
        reach = stats.attack.reach or 5
        prone = Condition.Prone

        feature = Feature(
            name="Cheap Shot",
            action=ActionType.BonusAction,
            description=f"{stats.selfref.capitalize()} attempts to strike a creature within {reach} ft with a cheap shot. The target must make a DC {dc} Strength or Dexterity save \
                (target's choice). On a failure, the target's speed is reduced to zero until the end of its next turn. A creature that is {prone.caption} makes this save at disadvantage.",
        )
        return [feature]


class _ExploitAdvantage(SneakyPower):
    def __init__(self):
        super().__init__(
            name="Deadeye Shot",
            source="A5E SRD Deadeye Shot",
            icon="target-laser",
            require_attack_types=AttackType.AllRanged(),
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Deadeye Shot",
            action=ActionType.BonusAction,
            uses=3,
            description=f"{stats.selfref.capitalize()} gains advantage on the next attack it makes until end of turn.",
        )
        return [feature]


CheapShot: Power = _CheapShot()
ExploitAdvantage: Power = _ExploitAdvantage()
FalseAppearance: Power = _FalseAppearance()
SneakyStrike: Power = _SneakyStrike()
Vanish: Power = _Vanish()


SneakyPowers: List[Power] = [
    CheapShot,
    ExploitAdvantage,
    FalseAppearance,
    SneakyStrike,
    Vanish,
]

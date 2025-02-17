from datetime import datetime
from math import ceil
from typing import List

from ...attack_template import natural, weapon
from ...attributes import Stats
from ...damage import AttackType
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


class RecklessPower(PowerWithStandardScoring):
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
            power_level=power_level,
            theme="reckless",
            power_type=PowerType.Theme,
            create_date=create_date,
            score_args=dict(
                require_attack_types=AttackType.AllMelee(),
                bonus_roles=MonsterRole.Bruiser,
                bonus_size=Size.Large,
                require_stats=Stats.STR,
                attack_names=[
                    "-",
                    natural.Claw,
                    natural.Bite,
                    natural.Tail,
                    natural.Lob,
                    natural.Slam,
                    weapon.Greataxe,
                    weapon.Greatsword,
                    weapon.Maul,
                ],
            )
            | score_args,
        )

    def modify_stats(self, stats: BaseStatblock) -> BaseStatblock:
        return stats.scale({Stats.WIS: -1})


class _Charger(RecklessPower):
    def __init__(self):
        super().__init__(
            name="Charger",
            source="Foe Foundry",
            power_level=LOW_POWER,
            bonus_size=Size.Large,
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class
        feature = Feature(
            name="Charge",
            action=ActionType.BonusAction,
            uses=1,
            description=f"{stats.selfref.capitalize()} charges and moves up to its speed. Up to one creature that is within 5 ft of the path \
                that the creature charges must make a DC {dc} Strength saving throw or be knocked **Prone**.",
        )
        return [feature]


class _Reckless(RecklessPower):
    def __init__(self):
        super().__init__(
            name="Reckless", source="SRD5.1 Reckless", require_roles=MonsterRole.Bruiser
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Reckless",
            description=f"At the start of their turn, {stats.selfref} can gain advantage on all melee weapon attack rolls made during this turn, but attack rolls against them have advantage until the start of their next turn.",
            action=ActionType.Feature,
        )
        return [feature]


class _BloodiedRage(RecklessPower):
    def __init__(self):
        super().__init__(
            name="Bloodied Rage",
            source="Foe Foundry",
            power_level=HIGH_POWER,
            require_cr=1,
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        threshold = easy_multiple_of_five(stats.hp.average / 2.0)
        feature = Feature(
            name="Bloodied Rage",
            description=f"When {stats.selfref}'s current hit points are below {threshold}, then it may make an extra attack as part of its Multiattack.",
            action=ActionType.Feature,
        )
        return [feature]


class _RelentlessEndurance(RecklessPower):
    def __init__(self):
        super().__init__(
            name="Relentless Endurance", source="SRD5.1 Half-Orc", power_level=LOW_POWER
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Relentless Endurance",
            description=f"When {stats.selfref} is reduced to 0 hit points, they can immediately make one melee attack as a reaction. If this attack hits, they regain 1 hit point.",
            action=ActionType.Reaction,
        )
        return [feature]


class _WildCleave(RecklessPower):
    def __init__(self):
        super().__init__(
            name="Wild Cleave", source="Foe Foundry", require_roles=MonsterRole.Bruiser
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        reach = (stats.attack.reach or 5) + 5
        push = 2 * reach

        feature = Feature(
            name="Wild Cleave",
            action=ActionType.Action,
            recharge=5,
            description=f"{stats.selfref.capitalize()} makes an attack against every creature within {reach} ft. On a hit, the creature is pushed up to {push} feet away.",
        )

        return [feature]


class _RecklessFlurry(RecklessPower):
    def __init__(self):
        super().__init__(
            name="Reckless Flurry",
            source="Foe Foundry",
            require_roles=MonsterRole.Bruiser,
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        attacks = max(3, int(ceil(1.5 * stats.multiattack)))
        attack_name = stats.attack.name

        feature = Feature(
            name="Reckless Flurry",
            action=ActionType.Action,
            recharge=5,
            description=f"{stats.selfref.capitalize()} makes a reckless flurry of {attacks} {attack_name} attacks. \
                Attacks against {stats.selfref} have advantage until the end of {stats.selfref}'s next turn.",
        )
        return [feature]


class _Toss(RecklessPower):
    def __init__(self):
        super().__init__(name="Toss", source="Foe Foundry", bonus_size=Size.Large)

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        size = stats.size.decrement()
        dmg = stats.target_value(0.7, force_die=Die.d6)
        distance = easy_multiple_of_five(3 * stats.cr, min_val=10, max_val=30)
        dc = stats.difficulty_class

        feature = Feature(
            name="Toss",
            action=ActionType.Action,
            replaces_multiattack=2,
            description=f"{stats.selfref.capitalize()} attempts to toss a {size} or smaller creature within 5 feet. The creature must make a DC {dc} Strength saving throw. \
                On a failure, it takes {dmg.description} bludgeoning damage and is thrown up to {distance} feet and falls **Prone**. If the thrown creature collides with another creature, then that other creature must make a DC {dc} Dexterity saving throw. \
                On a failure, the other creature takes half the damage.",
        )
        return [feature]


BloodiedRage: Power = _BloodiedRage()
Charger: Power = _Charger()
RecklessFlurry: Power = _RecklessFlurry()
Reckless: Power = _Reckless()
RelentlessEndurance: Power = _RelentlessEndurance()
Toss: Power = _Toss()
WildCleave: Power = _WildCleave()


RecklessPowers: List[Power] = [
    BloodiedRage,
    Charger,
    RecklessFlurry,
    Reckless,
    RelentlessEndurance,
    Toss,
    WildCleave,
]

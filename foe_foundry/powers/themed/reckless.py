from datetime import datetime
from math import ceil
from typing import List

from foe_foundry.references import action_ref

from ...attack_template import natural, weapon
from ...attributes import Stats
from ...damage import AttackType, Condition, DamageType
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
    PowerCategory,
    PowerWithStandardScoring,
)


class RecklessPower(PowerWithStandardScoring):
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
            power_level=power_level,
            theme="reckless",
            reference_statblock="Berserker",
            icon=icon,
            power_type=PowerCategory.Theme,
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

    def modify_stats_inner(self, stats: BaseStatblock) -> BaseStatblock:
        return stats.scale({Stats.WIS: -1})


class _Charger(RecklessPower):
    def __init__(self):
        super().__init__(
            name="Charger",
            source="Foe Foundry",
            icon="fast-forward-button",
            power_level=LOW_POWER,
            bonus_size=Size.Large,
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class
        prone = Condition.Prone
        dash = action_ref("Dash")
        feature = Feature(
            name="Charge",
            action=ActionType.BonusAction,
            uses=1,
            description=f"{stats.selfref.capitalize()} uses {dash} and moves towards a hostile creature. Up to one creature that is within 5 ft of the path \
                must make a DC {dc} Strength saving throw or be knocked {prone.caption}.",
        )
        return [feature]


class _Overrun(RecklessPower):
    def __init__(self):
        super().__init__(
            name="Overrun",
            source="Foe Foundry",
            icon="axe-swing",
            power_level=LOW_POWER,
            bonus_size=Size.Large,
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Overrun",
            action=ActionType.BonusAction,
            uses=1,
            description=f"Immediately after {stats.selfref} hits an enemy with an attack, it may move up to half its movement without triggering opportunity attacks. If it ends its movement next to another creature, it may make an attack against that creature.",
        )
        return [feature]


class _Reckless(RecklessPower):
    def __init__(self):
        super().__init__(
            name="Reckless",
            icon="saber-slash",
            source="SRD5.1 Reckless",
            require_roles=MonsterRole.Bruiser,
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
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
            icon="enrage",
            power_level=HIGH_POWER,
            require_cr=1,
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
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
            name="Relentless Endurance",
            icon="strong",
            source="SRD5.1 Half-Orc",
            power_level=LOW_POWER,
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Relentless Endurance",
            description=f"When {stats.selfref} is reduced to 0 hit points, they can immediately make one melee attack as a reaction. If this attack hits, they regain 1 hit point.",
            action=ActionType.Reaction,
        )
        return [feature]


class _WildCleave(RecklessPower):
    def __init__(self):
        super().__init__(
            name="Wild Cleave",
            icon="axe-swing",
            source="Foe Foundry",
            require_roles=MonsterRole.Bruiser,
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
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
            icon="wind-hole",
            require_roles=MonsterRole.Bruiser,
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        attacks = max(3, int(ceil(1.5 * stats.multiattack)))
        attack_name = stats.attack.display_name

        feature = Feature(
            name="Reckless Flurry",
            action=ActionType.Action,
            recharge=6,
            description=f"{stats.selfref.capitalize()} makes a reckless flurry of {attacks} {attack_name} attacks. \
                It may not hit the same target more than twice with this flurry. \
                Attacks against {stats.selfref} have advantage until the end of {stats.selfref}'s next turn.",
        )
        return [feature]


class _Toss(RecklessPower):
    def __init__(self):
        super().__init__(
            name="Toss", source="Foe Foundry", icon="arrow-dunk", bonus_size=Size.Large
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        if stats.size <= Size.Medium:
            size = stats.size
        else:
            size = stats.size.decrement()

        dmg = stats.target_value(
            target=1.5 if stats.multiattack >= 2 else 0.75, force_die=Die.d6
        )
        distance = easy_multiple_of_five(3 * stats.cr, min_val=10, max_val=30)
        dc = stats.difficulty_class
        prone = Condition.Prone

        feature = Feature(
            name="Toss",
            action=ActionType.Action,
            replaces_multiattack=2,
            description=f"{stats.selfref.capitalize()} attempts to toss a {size} or smaller creature within 5 feet. The creature must make a DC {dc} Strength saving throw. \
                On a failure, it takes {dmg.description} bludgeoning damage and is thrown up to {distance} feet and falls {prone.caption}. If the thrown creature collides with another creature, then that other creature must make a DC {dc} Dexterity saving throw. \
                On a failure, the other creature takes half the damage.",
        )
        return [feature]


class _Strangle(RecklessPower):
    def __init__(self):
        super().__init__(
            name="Strangle",
            source="A5E SRD - Bugbear",
            icon="slipknot",
            create_date=datetime(2023, 11, 23),
            attack_names=["-", weapon.Whip, natural.Slam, natural.Tentacle],
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        return []

    def modify_stats_inner(self, stats: BaseStatblock) -> BaseStatblock:
        dc = stats.difficulty_class_easy
        grappled = Condition.Grappled
        return stats.add_attack(
            name="Strangle",
            scalar=0.8,
            damage_type=DamageType.Bludgeoning,
            replaces_multiattack=1,
            additional_description=f"On a hit, the target is {grappled.caption} (escape DC {dc}) and is pulled 5 feet toward {stats.selfref}. \
                Until this grapple ends, {stats.selfref} automatically hits with its Strangle attack and the target can't breathe. \
                If the target attempts to cast a spell with a verbal component, it must succeed on a DC {dc} Constitution saving throw or the spell fails.",
        )


BloodiedRage: Power = _BloodiedRage()
Charger: Power = _Charger()
Overrun: Power = _Overrun()
RecklessFlurry: Power = _RecklessFlurry()
Reckless: Power = _Reckless()
RelentlessEndurance: Power = _RelentlessEndurance()
Strangle: Power = _Strangle()
Toss: Power = _Toss()
WildCleave: Power = _WildCleave()


RecklessPowers: List[Power] = [
    BloodiedRage,
    Charger,
    Overrun,
    RecklessFlurry,
    Reckless,
    RelentlessEndurance,
    Strangle,
    Toss,
    WildCleave,
]

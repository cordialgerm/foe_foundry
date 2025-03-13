from datetime import datetime
from math import ceil
from typing import List

from ...attack_template import natural, spell
from ...creature_types import CreatureType
from ...damage import AttackType, Bleeding, Condition, DamageType, Dazed, Swallowed
from ...die import Die, DieFormula
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


class MonstrousPower(PowerWithStandardScoring):
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
            theme="monstrous",
            power_type=PowerType.Theme,
            power_level=power_level,
            create_date=create_date,
            score_args=dict(
                require_types={CreatureType.Monstrosity, CreatureType.Beast}
            )
            | score_args,
        )


class _Constriction(MonstrousPower):
    def __init__(self):
        super().__init__(
            name="Constriction",
            source="SRD5.1 Giant Constrictor Snake",
            attack_names=["-", natural.Slam, natural.Tail],
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        reach = 5 if stats.size <= Size.Medium else 10
        dc = stats.difficulty_class
        dmg = DieFormula.target_value(max(2, ceil(stats.cr)), force_die=Die.d4)
        restrained = Condition.Restrained
        grappled = Condition.Grappled

        feature = Feature(
            name="Constrict",
            action=ActionType.Action,
            replaces_multiattack=1,
            description=f"{stats.selfref.capitalize()} chooses a target it can see within {reach} feet. The target must make a DC {dc} Strength saving throw or become {grappled.caption} (escape DC {dc}). \
                While grappled in this way, the target is also {restrained.caption} and takes {dmg.description} ongoing bludgeoning damage at the start of each of its turns.",
        )
        return [feature]


class _Swallow(MonstrousPower):
    def __init__(self):
        super().__init__(
            name="Swallow",
            source="Foe Foundry",
            power_level=HIGH_POWER,
            require_size=Size.Large,
            require_types={
                CreatureType.Monstrosity,
                CreatureType.Beast,
                CreatureType.Ooze,
            },
            attack_names={"-", natural.Bite},
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        return []

    def modify_stats_inner(self, stats: BaseStatblock) -> BaseStatblock:
        dc = stats.difficulty_class
        threshold = easy_multiple_of_five(3 * stats.cr, min_val=5, max_val=40)
        swallowed = Swallowed(
            damage=DieFormula.target_value(6 + stats.cr, force_die=Die.d4),
            regurgitate_dc=easy_multiple_of_five(
                threshold * 0.85, min_val=15, max_val=25
            ),
            regurgitate_damage_threshold=threshold,
        )

        stats = stats.add_attack(
            scalar=1.7,
            damage_type=DamageType.Piercing,
            attack_type=AttackType.MeleeNatural,
            replaces_multiattack=2,
            name="Swallow",
            additional_description=f"On a hit, the target must make a DC {dc} Dexterity saving throw. On a failure, it is {swallowed}",
        )
        return stats


class _Pounce(MonstrousPower):
    def __init__(self):
        super().__init__(name="Pounce", source="SRD5.1 Panther", power_level=LOW_POWER)

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class
        prone = Condition.Prone
        feature = Feature(
            name="Pounce",
            action=ActionType.Action,
            replaces_multiattack=1,
            description=f"{stats.selfref.capitalize()} jumps 20 feet toward a creature it can see, attempting to knock it prone. The target must make a DC {dc} Strength save or be knocked {prone.caption}.",
        )
        return [feature]


class _Corrosive(MonstrousPower):
    def __init__(self):
        super().__init__(
            name="Corrosive",
            source="SRD5.1 Rust Monster",
            power_level=HIGH_POWER,
            attack_names={
                "-",
                natural.Spit,
            },
            bonus_damage=DamageType.Acid,
        )

    def modify_stats_inner(self, stats: BaseStatblock) -> BaseStatblock:
        if stats.secondary_damage_type is None:
            stats = stats.copy(secondary_damage_type=DamageType.Acid)
        return stats

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class
        dmg = int(ceil(max(5, 2 * stats.cr)))
        feature = Feature(
            name="Corrode",
            action=ActionType.Action,
            replaces_multiattack=1,
            recharge=5,
            description=f"{stats.selfref.capitalize()} targets a creature within 30 feet that it can see and spits a glob of corrosive acid. \
                The target must make a DC {dc} Dexterity save. On a failure, the target takes {dmg} acid damage, and one non-magical metallic item the target carries begins to corrode. \
                If the object is a weapon, it takes a permanent and cumulative -1 penalty to damage rolls. If its penalty drops to -5, the weapon is destroyed. \
                If the object is either metal armor or a shield it takes a permanent and cumulative -1 penalty to the AC it offers. \
                Armor reduced to an AC of 10 or a shield that drops to a +0 bonus is destroyed.",
        )
        return [feature]


class _LingeringWound(MonstrousPower):
    def __init__(self):
        super().__init__(
            name="Lingering Wound",
            source="Foe Foundry",
            attack_names=[natural.Bite, natural.Claw, natural.Horns],
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dc = max(10, min(15, stats.difficulty_class_easy))
        dmg = stats.target_value(0.75, force_die=Die.d6)
        bleeding = Bleeding(damage=dmg, dc=dc)
        feature = Feature(
            name="Lingering Wound",
            action=ActionType.BonusAction,
            recharge=6,
            description=f"Immediately after hitting a creature, {stats.selfref} inflicts that creature with a lingering wound. \
                The creature gains {bleeding}",
        )
        return [feature]


class _Rampage(MonstrousPower):
    def __init__(self):
        super().__init__(name="Rampage", source="SRD5.1 Gnoll")

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Rampage",
            action=ActionType.Reaction,
            description=f"When a creature within 30 feet is reduced to 0 hitpoints, {stats.selfref} may move up to half its speed and make an attack.",
        )
        return [feature]


class _PetrifyingGaze(MonstrousPower):
    def __init__(self):
        super().__init__(
            name="Petrifying Gaze",
            source="SRD5.1 Basilisk",
            power_level=HIGH_POWER,
            require_types={
                CreatureType.Monstrosity,
                CreatureType.Celestial,
                CreatureType.Undead,
                CreatureType.Aberration,
            },
            bonus_roles={MonsterRole.Ambusher, MonsterRole.Controller},
            attack_names={"-", spell.Gaze},
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class_easy
        dazed = Dazed()
        petrified = Condition.Petrified

        feature = Feature(
            name="Petrifying Gaze",
            action=ActionType.Reaction,
            recharge=4,
            description=f"Whenever a creature within 60 feet looks at {stats.selfref}, it must make a DC {dc} Constitution saving throw. \
                On a failed save, the creature magically begins to turn to stone and is {dazed.caption}. It must repeat the saving throw at the end of its next turn. \
                On a success, the effect ends. On a failure, the creature is {petrified.caption} until it is freed by the *Greater Restoration* spell or other magic.",
        )
        return [feature]


class _JawClamp(MonstrousPower):
    def __init__(self):
        super().__init__(
            name="Jaw Clamp",
            source="A5E SRD Bulette",
            power_level=LOW_POWER,
            create_date=datetime(2023, 11, 24),
            attack_names=["-", natural.Bite],
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class_easy
        grappled = Condition.Grappled
        restrained = Condition.Restrained
        feature = Feature(
            name="Jaw Clamp",
            action=ActionType.Reaction,
            uses=1,
            description=f"When an attacker within 5 feet of {stats.selfref} misses it with a melee attack, {stats.selfref} makes a bite attack against the attacker. \
                On a hit, the attacker is {grappled.caption} (escape DC {dc}). Until this grapple ends, the grappled creature is {restrained.caption}, and the only attack {stats.selfref} can make is a bite against the grappled creature.",
        )
        return [feature]


class _Frenzy(MonstrousPower):
    def __init__(self):
        super().__init__(
            name="Frenzy",
            source="A5E SRD Cockatrice",
            power_level=LOW_POWER,
            create_date=datetime(2023, 11, 24),
            require_attack_types=AttackType.AllMelee(),
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Frenzy",
            action=ActionType.Reaction,
            uses=2,
            description=f"When attacked by a creature it can see within 20 feet, {stats.selfref} moves up to half its Speed and makes an attack against that creature.",
        )
        return [feature]


class _TearApart(MonstrousPower):
    def __init__(self):
        super().__init__(
            name="Tear Apart",
            source="A5E SRD Glabrezu",
            power_level=HIGH_POWER,
            create_date=datetime(2023, 11, 24),
            attack_names=["-", natural.Claw],
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class_easy
        grappled = Condition.Grappled
        feature1 = Feature(
            name="Claw Grapple",
            action=ActionType.Feature,
            modifies_attack=True,
            hidden=True,
            description=f"On a hit, the target is {grappled.caption} (escape DC {dc})",
        )

        dmg = stats.target_value(dpr_proportion=0.8, force_die=Die.d10)

        feature2 = Feature(
            name="Tear Apart",
            action=ActionType.Action,
            description=f"{stats.selfref} rips at a target it is grappling, releasing the grapple. The creature must make a DC {dc} Strength saving throw, \
                taking {dmg} slashing damage on a failure and half as much on a success. If this damage reduces a creature to 0 hit points, it dies and is torn in half.",
        )

        return [feature1, feature2]


Constriction: Power = _Constriction()
Corrosive: Power = _Corrosive()
Frenzy: Power = _Frenzy()
JawClamp: Power = _JawClamp()
LingeringWound: Power = _LingeringWound()
PetrifyingGaze: Power = _PetrifyingGaze()
Pounce: Power = _Pounce()
Rampage: Power = _Rampage()
Swallow: Power = _Swallow()
TearApart: Power = _TearApart()


MonstrousPowers: List[Power] = [
    Constriction,
    Corrosive,
    Frenzy,
    JawClamp,
    LingeringWound,
    PetrifyingGaze,
    Pounce,
    Rampage,
    Swallow,
    TearApart,
]

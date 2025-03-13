from datetime import datetime
from typing import List

import numpy as np

from ...attack_template import natural as natural_attacks
from ...creature_types import CreatureType
from ...damage import AttackType, Condition, DamageType
from ...die import Die
from ...features import ActionType, Feature
from ...statblocks import BaseStatblock
from ...utils import easy_multiple_of_five, summoning
from ..power import HIGH_POWER, MEDIUM_POWER, Power, PowerType, PowerWithStandardScoring


class DraconicPower(PowerWithStandardScoring):
    def __init__(
        self,
        name: str,
        source: str,
        power_level: float = MEDIUM_POWER,
        create_date: datetime | None = None,
        **score_args,
    ):
        standard_score_args = dict(require_types=CreatureType.Dragon, **score_args)
        super().__init__(
            name=name,
            power_type=PowerType.CreatureType,
            source=source,
            power_level=power_level,
            create_date=create_date,
            theme="Dragon",
            score_args=standard_score_args,
        )


class _FrightfulGaze(DraconicPower):
    def __init__(self):
        super().__init__(name="Frightful Gaze", source="Foe Foundry")

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class
        dmg = int(max(3, stats.cr / 2))
        frightened = Condition.Frightened

        feature = Feature(
            name="Fearsome Gaze",
            action=ActionType.Reaction,
            uses=3,
            description=f"Whenever a creature within 60 feet of {stats.selfref} looks at {stats.selfref}, it must make a DC {dc} Wisdom save or be {frightened.caption} of {stats.selfref} (save ends at end of turn). \
                While frightened in this way, each time the target takes damage, they take an additional {dmg} psychic damage.",
        )
        return [feature]


class _TailSwipe(DraconicPower):
    def __init__(self):
        super().__init__(
            name="Tail Swipe",
            source="A5E SRD Ancient Red Dragon",
            attack_names=natural_attacks.Tail,
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Tail Swipe",
            action=ActionType.Reaction,
            description=f"When a creature {stats.selfref} can see within 10 feet hits {stats.selfref} with a melee attack, {stats.selfref} makes a Tail Attack against it.",
        )
        return [feature]

    def modify_stats_inner(self, stats: BaseStatblock) -> BaseStatblock:
        if stats.attack.name == natural_attacks.Tail.attack_name:
            return stats

        stats = stats.add_attack(
            scalar=0.8,
            damage_type=DamageType.Bludgeoning,
            die=Die.d8,
            name="Tail Attack",
            attack_type=AttackType.MeleeNatural,
            reach=10,
            additional_description="On a hit, the target is pushed up to 10 feet away.",
        )

        return stats


class _WingBuffet(DraconicPower):
    def __init__(self):
        super().__init__(
            name="Wing Buffet",
            source="5.1 SRD Ancient Red Dragon",
            bonus_cr=7,
            require_flying=True,
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dmg = stats.target_value(0.5, suggested_die=Die.d6)
        dc = stats.difficulty_class_easy
        prone = Condition.Prone
        feature = Feature(
            name="Wing Buffet",
            action=ActionType.Action,
            replaces_multiattack=1,
            description=f"{stats.selfref.capitalize()} beats its wings. Each other creature within 10 feet must make a DC {dc} Strength saving throw. \
                On a failure, the creature takes {dmg.description} bludgeoning damage and is knocked {prone.caption}. On a success, the creature takes half damage and is not knocked prone. \
                The dragon then flies up to half its movement speed. This movement does not trigger attacks of opportunity from prone targets.",
        )

        return [feature]


class _DragonsGreed(DraconicPower):
    def __init__(self):
        super().__init__(name="Dragon's Greed", source="Foe Foundry")

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class_easy
        charmed = Condition.Charmed
        feature = Feature(
            name="Dragon's Greed",
            action=ActionType.Action,
            replaces_multiattack=2,
            description=f"{stats.selfref.capitalize()} targets a creature it can see within 60 feet, preferring to target the creature in posession of the most valuable treasure or magical items. \
                The creature must make a DC {dc} Charisma saving throw or be {charmed.caption} by {stats.selfref} (save ends at end of turn). While charmed in this way, the creature must use its movement and action \
                to approach {stats.selfref} and make it an offering of its most valuable treasure or magical item. The target uses its action to place the offering on the floor at its feet.",
        )
        return [feature]


def _draconic_minions(stats: BaseStatblock) -> str | None:
    # TODO - remove the randomness here
    rng = np.random.default_rng(20220518)
    desired_summon_cr = stats.cr / 2.5
    damage_type = stats.secondary_damage_type
    if damage_type is None:
        return None

    try:
        _, _, description = summoning.determine_summon_formula(
            summoner=[stats.creature_type, damage_type],
            summon_cr_target=desired_summon_cr,
            rng=rng,
        )
        return description
    except ValueError:
        return None


def _check_draconic_minions(stats: BaseStatblock) -> bool:
    v = _draconic_minions(stats)
    return v is not None


class _DraconicMinions(DraconicPower):
    def __init__(self):
        super().__init__(
            name="Draconic Minions",
            source="Foe Foundry",
            power_level=HIGH_POWER,
            require_cr=7,
            require_callback=_check_draconic_minions,
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        damage_type = stats.secondary_damage_type
        if damage_type is None:
            raise ValueError("dragon does not have a secondary damage type")

        description = _draconic_minions(stats)
        if description is None:
            raise ValueError("Dragon has no minions available")

        feature = Feature(
            name="Draconic Minions",
            action=ActionType.Action,
            uses=1,
            description=f"{stats.selfref.capitalize()} roars, summoning its minions to its aid. {description}",
        )

        return [feature]


class _VengefulBreath(DraconicPower):
    def __init__(self):
        super().__init__(
            name="Vengeful Breath",
            source="A5E SRD Behir",
            create_date=datetime(2023, 11, 22),
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        hp = easy_multiple_of_five(stats.hp.average / 2)
        feature = Feature(
            name="Vengeful Breath",
            action=ActionType.Reaction,
            uses=1,
            description=f"When {stats.selfref} is hit by a melee attack and is below {hp} hp it immediately recharges or regains a charge on an ability of its choice. \
                It may also make an attack against the attacker with advantage.",
        )
        return [feature]


DragonsGreed: Power = _DragonsGreed()
DraconicMinions: Power = _DraconicMinions()
FrightfulGaze: Power = _FrightfulGaze()
TailSwipe: Power = _TailSwipe()
VengefulBreath: Power = _VengefulBreath()
WingBuffet: Power = _WingBuffet()

DragonPowers: List[Power] = [
    DragonsGreed,
    DraconicMinions,
    FrightfulGaze,
    TailSwipe,
    VengefulBreath,
    WingBuffet,
]

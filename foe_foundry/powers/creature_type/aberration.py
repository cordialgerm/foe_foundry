from datetime import datetime
from math import floor
from typing import List

from ...attack_template import natural, spell
from ...creature_types import CreatureType
from ...damage import AttackType, Condition, DamageType, Swallowed, conditions
from ...die import Die, DieFormula
from ...features import ActionType, Feature
from ...size import Size
from ...statblocks import BaseStatblock
from ...utils import easy_multiple_of_five
from ..power import HIGH_POWER, MEDIUM_POWER, Power, PowerType, PowerWithStandardScoring


class AberrationPower(PowerWithStandardScoring):
    def __init__(
        self,
        name: str,
        source: str,
        power_level: float = MEDIUM_POWER,
        create_date: datetime | None = None,
        **score_args,
    ):
        standard_score_args = dict(require_types=CreatureType.Aberration)
        standard_score_args.update(score_args)

        super().__init__(
            name=name,
            source=source,
            power_type=PowerType.CreatureType,
            power_level=power_level,
            create_date=create_date,
            score_args=standard_score_args,
            theme="Aberration",
            reference_statblock="Aboleth",
        )


class _TentacleGrapple(AberrationPower):
    def __init__(self):
        super().__init__(
            name="Tentacle Grapple",
            source="Foe Foundry",
            attack_names={"-", natural.Tentacle},
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dc = int(floor(11 + 0.5 * stats.cr))
        grappled = Condition.Grappled
        restrained = Condition.Restrained
        feature = Feature(
            name="Tentacle Grapple",
            description=f"On a hit, the target is {grappled.caption} (escape DC {dc}). While grappled in this way, the target is {restrained.caption}.",
            action=ActionType.Feature,
            modifies_attack=True,
            hidden=True,
        )
        return [feature]


class _GazeOfTheFarRealm(AberrationPower):
    def __init__(self):
        super().__init__(
            name="Gaze of the Far Realm",
            source="Foe Foundry",
            create_date=datetime(2023, 11, 21),
            attack_names=spell.Gaze,
            bonus_damage=DamageType.Psychic,
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class
        dmg = stats.target_value(0.25, suggested_die=Die.d6)
        burning = conditions.Burning(damage=dmg, damage_type=DamageType.Psychic)
        frightened = Condition.Frightened
        dazed = conditions.Dazed()
        feature = Feature(
            name="Gaze of the Far Realm",
            action=ActionType.Action,
            recharge=4,
            replaces_multiattack=1,
            description=f"One target that {stats.selfref} can see within 60 feet must succed on a DC {dc} Charisma saving throw. \
                On a failure, roll a d6. On a 1-2, the creature is {frightened.caption} (save ends at end of turn). \
                On a 3-4, the creature is {dazed.caption} (save ends at end of turn). \
                On a 5-6, the creature is {burning.caption}. {burning.description_3rd}.",
        )
        return [feature]


class _MaddeningWhispers(AberrationPower):
    def __init__(self):
        super().__init__(
            name="Maddening Whispers",
            source="5.1 SRD (Gibbering Mouther)",
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class_easy
        feature = Feature(
            name="Madenning Whispers",
            action=ActionType.Feature,
            description=f"Each creature that starts its turn within 20 ft of {stats.selfref} must make a DC {dc} Wisdom saving throw. \
                On a failure, the creature can't take reactions until the start of its next turn and rolls a d8 to determine what it does during its turn. \
                On a 1-4, the creature does nothing. On a 5-6, the creature takes no action or bonus action and uses all its movement to move in a randomly determined direction. \
                On a 7-8, the creature makes a melee attack against a randomly determined creature within its reach or does nothing if it can't make such an attack.",
        )
        return [feature]


class _TentacleSlam(AberrationPower):
    def __init__(self):
        super().__init__(
            name="Tentacle Slam",
            source="Foe Foundry",
            attack_names={"-", natural.Tentacle},
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class_easy
        dmg = stats.target_value(0.5, suggested_die=Die.d6)
        grappled = Condition.Grappled
        stunned = Condition.Stunned
        feature = Feature(
            name="Tentacle Slam",
            action=ActionType.Action,
            replaces_multiattack=2,
            description=f"{stats.selfref.capitalize()} makes an attack against a creature within its reach. If the attack hits, the target is {grappled.caption} (escape DC {dc}). \
                Then, {stats.selfref} slams each creature grappled by it into each other or a solid surface. \
                Each creature must succeed on a DC {dc} Constitution saving throw or take {dmg.description} bludgeoning damage and be {stunned.caption} until the end of {stats.selfref}'s next turn.",
        )
        return [feature]


class _NullificationMaw(AberrationPower):
    def __init__(self):
        super().__init__(
            name="Nullification Maw",
            source="Foe Foundry",
            power_level=HIGH_POWER,
            require_size=Size.Large,
            attack_names={"-", natural.Bite},
        )

    def modify_stats_inner(self, stats: BaseStatblock) -> BaseStatblock:
        dc = stats.difficulty_class
        threshold = easy_multiple_of_five(2 * stats.cr, min_val=5, max_val=40)
        swallowed = Swallowed(
            damage=DieFormula.target_value(5 + stats.cr, force_die=Die.d4),
            regurgitate_dc=easy_multiple_of_five(
                threshold * 0.75, min_val=15, max_val=25
            ),
            regurgitate_damage_threshold=threshold,
        )
        stats = stats.add_attack(
            scalar=1.5,
            damage_type=DamageType.Piercing,
            attack_type=AttackType.MeleeNatural,
            replaces_multiattack=2,
            name="Swallow",
            additional_description=f"On a hit, the target must make a DC {dc} Dexterity saving throw. On a failure, it is {swallowed} Also see *Nullification Maw*.",
        )
        return stats

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Nullification Maw",
            action=ActionType.Feature,
            description=f"Magical effects, including those produced by spells and magic items but excluding those created by artifacts or deities, are suppressed inside {stats.selfref}'s gullet. \
                Any spell slot or charge expended by a creature in the gullet to cast a spell or activate a property of a magic item is wasted. \
                No spell or magical effect that originates outside {stats.selfref}'s gullet, except one created by an artifact or a deity, can affect a creature or an object inside the gullet.",
        )
        return [feature]


GazeOfTheFarRealm: Power = _GazeOfTheFarRealm()
MadenningWhispers: Power = _MaddeningWhispers()
NullificationMaw: Power = _NullificationMaw()
TentacleGrapple: Power = _TentacleGrapple()
TentacleSlam: Power = _TentacleSlam()

AberrationPowers: List[Power] = [
    GazeOfTheFarRealm,
    MadenningWhispers,
    NullificationMaw,
    TentacleGrapple,
    TentacleSlam,
]

from math import ceil, floor
from typing import Dict, List, Tuple

from numpy.random import Generator

from foe_foundry.features import Feature
from foe_foundry.statblocks import BaseStatblock

from ...attack_template import natural, spell
from ...creature_types import CreatureType
from ...damage import AttackType, DamageType, Swallowed, conditions
from ...die import Die, DieFormula
from ...features import ActionType, Feature
from ...size import Size
from ...statblocks import BaseStatblock
from ...utils import easy_multiple_of_five
from ..power import HIGH_POWER, Power, PowerType
from ..scoring import AttackNames, score


def score_aberration(
    candidate: BaseStatblock,
    min_size: Size | None = None,
    attack_names: AttackNames = None,
) -> float:
    return score(
        candidate=candidate,
        require_types=CreatureType.Aberration,
        require_size=min_size,
        attack_names=attack_names,
    )


class _TentacleGrapple(Power):
    def __init__(self):
        super().__init__(
            name="Tentacle Grapple", source="FoeFoundryOriginal", power_type=PowerType.Creature
        )

    def score(self, candidate: BaseStatblock) -> float:
        return score_aberration(
            candidate,
            attack_names={"-", natural.Tentacle},
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dc = int(floor(11 + 0.5 * stats.cr))
        feature = Feature(
            name="Tentacle Grapple",
            description=f"On a hit, the target is **Grappled** (escape DC {dc}). While grappled in this way, the target is **Restrained**.",
            action=ActionType.Feature,
            modifies_attack=True,
            hidden=True,
        )
        return [feature]


class _GazeOfTheFarRealm(Power):
    def __init__(self):
        super().__init__(
            name="Gaze of the Far Realm",
            source="FoeFoundryOriginal",
            power_type=PowerType.Creature,
        )

    def score(self, candidate: BaseStatblock) -> float:
        return score_aberration(candidate, attack_names=spell.Gaze)

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class
        dmg = DieFormula.target_value(0.25 * stats.attack.average_damage, suggested_die=Die.d6)
        burning = conditions.Burning(damage=dmg, damage_type=DamageType.Psychic)
        feature = Feature(
            name="Gaze of the Far Realm",
            action=ActionType.Action,
            recharge=4,
            replaces_multiattack=1,
            description=f"One target that {stats.selfref} can see within 60 feet must succed on a DC {dc} Charisma saving throw. \
                On a failure, roll a d6. On a 1-2, the creature is **Frightened** (save ends at end of turn). \
                On a 3-4, the creature is **Dazed** (save ends at end of turn). \
                On a 5-6, the creature is {burning.caption}. {burning.description_3rd}.",
        )
        return [feature]


class _MaddeningWhispers(Power):
    def __init__(self):
        super().__init__(
            name="Maddening Whispers",
            source="5.1 SRD (Gibbering Mouther)",
            power_type=PowerType.Theme,
        )

    def score(self, candidate: BaseStatblock) -> float:
        return score_aberration(candidate)

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


class _TentacleSlam(Power):
    def __init__(self):
        super().__init__(
            name="Tentacle Slam", source="FoeFoundryOriginal", power_type=PowerType.Creature
        )

    def score(self, candidate: BaseStatblock) -> float:
        return score_aberration(
            candidate,
            attack_names={"-", natural.Tentacle},
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class_easy
        dmg = DieFormula.target_value(0.5 * stats.attack.average_damage, suggested_die=Die.d6)

        feature = Feature(
            name="Tentacle Slam",
            action=ActionType.Action,
            replaces_multiattack=2,
            description=f"{stats.selfref.capitalize()} makes an attack against a creature within its reach. If the attack hits, the target is **Grappled** (escape DC {dc}). \
                Then, {stats.selfref} slams each creature grappled by it into each other or a solid surface. \
                Each creature must succeed on a DC {dc} Constitution saving throw or take {dmg.description} bludgeoning damage and be **Stunned** until the end of {stats.selfref}'s next turn.",
        )
        return [feature]


class _NullificationMaw(Power):
    def __init__(self):
        super().__init__(
            name="Nullification Maw",
            power_type=PowerType.Theme,
            source="FoeFoundryOriginal",
            power_level=HIGH_POWER,
        )

    def score(self, candidate: BaseStatblock) -> float:
        return score_aberration(
            candidate,
            min_size=Size.Large,
            attack_names={"-", natural.Bite},
        )

    def modify_stats(self, stats: BaseStatblock) -> BaseStatblock:
        stats, _ = self._helper(stats)
        return stats

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        _, feature = self._helper(stats)
        return [feature]

    def _helper(self, stats: BaseStatblock) -> Tuple[BaseStatblock, Feature]:
        dc = stats.difficulty_class
        threshold = easy_multiple_of_five(2 * stats.cr, min_val=5, max_val=40)
        swallowed = Swallowed(
            damage=DieFormula.target_value(5 + stats.cr, force_die=Die.d4),
            regurgitate_dc=easy_multiple_of_five(threshold * 0.75, min_val=15, max_val=25),
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

        feature = Feature(
            name="Nullification Maw",
            action=ActionType.Feature,
            description=f"Magical effects, including those produced by spells and magic items but excluding those created by artifacts or deities, are suppressed inside {stats.selfref}'s gullet. \
                Any spell slot or charge expended by a creature in the gullet to cast a spell or activate a property of a magic item is wasted. \
                No spell or magical effect that originates outside {stats.selfref}'s gullet, except one created by an artifact or a deity, can affect a creature or an object inside the gullet.",
        )

        return stats, feature


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

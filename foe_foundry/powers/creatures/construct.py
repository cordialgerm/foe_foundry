from math import ceil
from typing import Dict, List, Tuple

from num2words import num2words
from numpy.random import Generator

from foe_foundry.features import Feature
from foe_foundry.powers.power_type import PowerType
from foe_foundry.statblocks import BaseStatblock

from ...attack_template import natural as natural_attacks
from ...attributes import Skills, Stats
from ...creature_types import CreatureType
from ...damage import AttackType, DamageType
from ...die import Die, DieFormula
from ...features import ActionType, Feature
from ...powers.power_type import PowerType
from ...statblocks import BaseStatblock, MonsterDials
from ...utils import easy_multiple_of_five
from ..attack_modifiers import AttackModifiers, resolve_attack_modifier
from ..power import Power, PowerType
from ..scores import (
    EXTRA_HIGH_AFFINITY,
    HIGH_AFFINITY,
    LOW_AFFINITY,
    MODERATE_AFFINITY,
    NO_AFFINITY,
)


def _score(candidate: BaseStatblock, attack_modifiers: AttackModifiers = None) -> float:
    if candidate.creature_type != CreatureType.Construct:
        return NO_AFFINITY

    score = HIGH_AFFINITY
    score += resolve_attack_modifier(candidate, attack_modifiers)

    return score if score > 0 else NO_AFFINITY


class _ConstructedGuardian(Power):
    def __init__(self):
        super().__init__(name="Constructed Guardian", power_type=PowerType.Creature)

    def score(self, candidate: BaseStatblock) -> float:
        return _score(candidate)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        feature = Feature(
            name="Constructed Guardian",
            action=ActionType.Feature,
            description="This creature can make opportunity attacks without using a reaction.",
        )

        return stats, feature


class _ArmorPlating(Power):
    """Armor Plating (Trait). This creature has a +2 bonus to Armor Class.
    Each time the creature's hit points are reduced by one-quarter of their maximum value,
    this bonus decreases by 1, to a maximum penalty to Armor Class of -2."""

    def __init__(self):
        super().__init__(name="Armor Plating", power_type=PowerType.Creature)

    def score(self, candidate: BaseStatblock) -> float:
        return _score(candidate)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        stats = stats.apply_monster_dials(MonsterDials(ac_modifier=2))

        hp = easy_multiple_of_five(0.2 * stats.hp.average)

        feature = Feature(
            name="Armor Plating",
            action=ActionType.Feature,
            description=f"This creature has a +2 bonus to AC (included in AC). \
                Each time it takes {hp} or more damage in a single turn its AC is reduced by 1",
        )

        return stats, feature


class _ImmutableForm(Power):
    def __init__(self):
        super().__init__(name="Immutable Form", power_type=PowerType.Creature)

    def score(self, candidate: BaseStatblock) -> float:
        return _score(candidate)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        feature = Feature(
            name="Immutable Form",
            action=ActionType.Feature,
            description=f"{stats.selfref.capitalize()} is immune to any spell or effect that would alter its form",
        )

        return stats, feature


class _BoundProtector(Power):
    def __init__(self):
        super().__init__(name="Bound Protector", power_type=PowerType.Creature)

    def score(self, candidate: BaseStatblock) -> float:
        return _score(candidate)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        feature = Feature(
            name="Bound Protector",
            action=ActionType.Feature,
            description=f"{stats.selfref.capitalize()} is magically bound to protect another friendly creature. \
                If {stats.selfref} is within 60 feet of its ward, then half of any damage the ward takes (rounded up) is transferred to {stats.selfref}",
        )

        return stats, feature


class _ExplosiveCore(Power):
    def __init__(self):
        super().__init__(name="Explosive Core", power_type=PowerType.Creature)

    def score(self, candidate: BaseStatblock) -> float:
        return _score(candidate)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        dmg_type = stats.secondary_damage_type or DamageType.Fire
        dmg = DieFormula.target_value(1.5 * stats.attack.average_damage, suggested_die=Die.d6)
        dc = stats.difficulty_class_easy

        feature = Feature(
            name="Explosive Core",
            action=ActionType.Reaction,
            description=f"When {stats.selfref} is destroyed, it explodes with {dmg_type} energy. Each creature within 10 feet must make a DC {dc} Dexterity saving throw, \
                taking {dmg.description} {dmg_type} damage on a failure or half on a success.",
        )

        return stats, feature


class _Smother(Power):
    def __init__(self):
        super().__init__(name="Smother", power_type=PowerType.Creature)

    def score(self, candidate: BaseStatblock) -> float:
        return _score(
            candidate,
            attack_modifiers={
                natural_attacks.Slam: HIGH_AFFINITY,
                "*": NO_AFFINITY,
            },
        )

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        dc = stats.difficulty_class_easy

        smother_attack = stats.attack.scale(
            scalar=0.5,
            damage_type=DamageType.Bludgeoning,
            attack_type=AttackType.MeleeWeapon,
            die=Die.d6,
            name="Smother",
        )
        dmg = smother_attack.damage.formula
        smother_attack = smother_attack.copy(
            additional_description=f"On a hit, {stats.selfref} begins to smother the target. The creature is **Grappled** (escape DC {dc}). \
                While grappled this way, the creature is **Restrained**, **Blinded**, and suffers {dmg.description} ongoing bludgeoning damage at the start of each of its turns.",
        )

        stats = stats.add_attack(smother_attack)

        feature = Feature(
            name="Damage Transfer",
            action=ActionType.Feature,
            description=f"While it is grappling a creature, {stats.selfref} takes only half the damage dealt to it, and the creature grappled by {stats.selfref} takes the other half.",
        )

        return stats, feature


class _Retrieval(Power):
    def __init__(self):
        super().__init__(name="Retrieval", power_type=PowerType.Creature)

    def score(self, candidate: BaseStatblock) -> float:
        return _score(
            candidate, attack_modifiers={"*": NO_AFFINITY, natural_attacks.Slam: HIGH_AFFINITY}
        )

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, List[Feature]]:
        dc = stats.difficulty_class_easy
        feature1 = Feature(
            name="Paralyzing Beam",
            recharge=5,
            action=ActionType.Action,
            replaces_multiattack=2,
            description=f"{stats.selfref.capitalize()} targets one creature it can see within 60 ft. The target must succeed on a DC {dc} Constitution saving throw or be **Paralyzed** for 1 minute (save ends at end of turn).  \
                If the paralyzed creature is Medium or smaller, {stats.selfref} can pick it up as part of its move and move at its full speed.",
        )

        feature2 = Feature(
            name="Retrieval",
            uses=3,
            action=ActionType.Action,
            description=f"{stats.selfref.capitalize()} casts *Plane Shift* on itself and up to one **Incapacitated** or **Grappled** creature, which is considered willing.",
        )

        return stats, [feature1, feature2]


class _SpellStoring(Power):
    def __init__(self):
        super().__init__(name="Spell Storing", power_type=PowerType.Creature)

    def score(self, candidate: BaseStatblock) -> float:
        return _score(candidate)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        dc = stats.difficulty_class

        level = min(4, int(ceil(stats.cr / 2.5)))
        examples_by_level = [
            "*Burning Hands* or *Bane*",
            "*Web*, *Hold Person*, or *Levitate*",
            "*Slow*, *Dispel Magic*, or *Lightning Bolt*",
            "*Confusion*, *Fire Shield*, or *Greater Invisibility*",
        ]
        examples = examples_by_level[level - 1]
        level_text = num2words(level, to="ordinal")

        feature = Feature(
            name="Spell Storing",
            action=ActionType.Action,
            description=f"{stats.selfref.capitalize()} stores a single spell of {level_text} level or lower. {stats.selfref} may cast the spell using a spell save DC of {dc}. \
                When the spell is cast or a new spell is stored, any previously stored spell is lost. Some example spells include {examples}.",
        )

        return stats, feature


ArmorPlating: Power = _ArmorPlating()
BoundProtector: Power = _BoundProtector()
ExplosiveCore: Power = _ExplosiveCore()
ImmutableForm: Power = _ImmutableForm()
Retrieval: Power = _Retrieval()
ConstructedGuardian: Power = _ConstructedGuardian()
Smother: Power = _Smother()
SpellStoring: Power = _SpellStoring()

ConstructPowers: List[Power] = [
    ArmorPlating,
    BoundProtector,
    ExplosiveCore,
    ImmutableForm,
    Retrieval,
    ConstructedGuardian,
    Smother,
    SpellStoring,
]

from math import ceil
from typing import List, Tuple

from num2words import num2words
from numpy.random import Generator

from foe_foundry.features import Feature
from foe_foundry.statblocks import BaseStatblock

from ...attack_template import natural as natural_attacks
from ...creature_types import CreatureType
from ...damage import Attack, AttackType, DamageType
from ...die import Die, DieFormula
from ...features import ActionType, Feature
from ...role_types import MonsterRole
from ...statblocks import BaseStatblock, MonsterDials
from ...utils import easy_multiple_of_five
from ..power import (
    HIGH_POWER,
    LOW_POWER,
    MEDIUM_POWER,
    Power,
    PowerType,
    PowerWithStandardScoring,
)


class ConstructPower(PowerWithStandardScoring):
    def __init__(self, name: str, source: str, power_level: float = MEDIUM_POWER, **score_args):
        standard_score_args = dict(require_types=CreatureType.Construct, **score_args)
        super().__init__(
            name=name,
            power_type=PowerType.Creature,
            source=source,
            power_level=power_level,
            score_args=standard_score_args,
        )


class _ConstructedGuardian(ConstructPower):
    def __init__(self):
        super().__init__(
            name="Constructed Guardian",
            source="FoeFoundryOriginal",
            power_level=LOW_POWER,
            bonus_roles=MonsterRole.Defender,
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Constructed Guardian",
            action=ActionType.Feature,
            description=f"If {stats.selfref.capitalize()} is within 10 feet of an objective (creature, location, or object) that was designed to guard, it has advantage on attack rolls.",
        )
        return [feature]


class _ProtectivePlating(ConstructPower):
    def __init__(self):
        super().__init__(
            name="Protective Plating", source="FoeFoundryOriginal", power_level=LOW_POWER
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class
        feature = Feature(
            name="Protective Plating",
            action=ActionType.Reaction,
            description=f"When {stats.selfref} is hit by an attack, it gains resistance to all damage until the beginning of its next turn. \
                          Then, {stats.selfref} must make a DC {dc} Constitution saving throw. On a failure, the protective plating is destroyed and this reaction no longer functions. \
                          If {stats.selfref} is hit by a critical hit, the protective plating is also destroyed.",
        )

        return [feature]


class _ImmutableForm(ConstructPower):
    def __init__(self):
        super().__init__(
            name="Immutable Form", source="SRD 5.1 Stone Golem", power_level=LOW_POWER
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Immutable Form",
            action=ActionType.Feature,
            description=f"{stats.selfref.capitalize()} is immune to any spell or effect that would alter its form",
        )
        return [feature]


class _BoundProtector(ConstructPower):
    def __init__(self):
        super().__init__(
            name="Bound Protector",
            source="SRD 5.1 Shield Guardian",
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Bound Protector",
            action=ActionType.Feature,
            description=f"{stats.selfref.capitalize()} is magically bound to protect another friendly creature. \
                If {stats.selfref} is within 60 feet of its ward, then half of any damage the ward takes (rounded up) is transferred to {stats.selfref}",
        )
        return [feature]


class _ExplosiveCore(ConstructPower):
    def __init__(self):
        super().__init__(
            name="Explosive Core", source="FoeFoundryOriginal", bonus_damage=DamageType.Fire
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dmg_type = DamageType.Fire
        dmg = DieFormula.target_value(1.5 * stats.attack.average_damage, suggested_die=Die.d6)
        dc = stats.difficulty_class_easy

        feature = Feature(
            name="Explosive Core",
            action=ActionType.Reaction,
            description=f"When {stats.selfref} is destroyed, it explodes with {dmg_type} energy. Each creature within 10 feet must make a DC {dc} Dexterity saving throw, \
                taking {dmg.description} {dmg_type} damage on a failure or half on a success.",
        )

        return [feature]


class _Smother(ConstructPower):
    def __init__(self):
        super().__init__(
            name="Smother",
            source="SRD 5.1 Rug of Smothering",
            attack_names={"-", natural_attacks.Slam},
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Damage Transfer",
            action=ActionType.Feature,
            description=f"While it is grappling a creature, {stats.selfref} takes only half the damage dealt to it, and the creature grappled by {stats.selfref} takes the other half.",
        )
        return [feature]

    def modify_stats(self, stats: BaseStatblock) -> BaseStatblock:
        dc = stats.difficulty_class_easy

        def set_on_hit(attack: Attack) -> Attack:
            dmg = attack.damage.formula
            additional_description = f"On a hit, {stats.selfref} begins to smother the target. The creature is **Grappled** (escape DC {dc}). \
                While grappled this way, the creature is **Restrained**, **Blinded**, and suffers {dmg.description} ongoing bludgeoning damage at the start of each of its turns."
            return attack.copy(additional_description=additional_description)

        stats = stats.add_attack(
            scalar=0.5,
            damage_type=DamageType.Bludgeoning,
            attack_type=AttackType.MeleeWeapon,
            die=Die.d6,
            name="Smother",
            callback=set_on_hit,
        )

        return stats


class _Retrieval(ConstructPower):
    def __init__(self):
        super().__init__(
            name="Retrieval",
            source="FoeFoundryOriginal",
            power_level=HIGH_POWER,
            require_cr=7,
            attack_names=["-", natural_attacks.Slam],
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class

        feature1 = Feature(
            name="Pursue Objective",
            action=ActionType.Feature,
            description=f"{stats.selfref.capitalize()} was designed to retrieve a specific objective (creature or object). It always knows the location and direction of its objective if it is on the same plane of existence.",
        )

        feature2 = Feature(
            name="Acquire Objective",
            recharge=5,
            action=ActionType.Action,
            replaces_multiattack=2,
            description=f"{stats.selfref.capitalize()} targets one object or creature it can see within 60 ft. The target must succeed on a DC {dc} Constitution saving throw. \
                If the object is not being carried, it automatically fails this save. If the object is being carried, the creature carrying it makes the save. \
                On a failure, the target is teleported onto {stats.selfref}'s back and is **Grappled** (escape DC {dc}) and **Paralyzed** for 1 minute (save ends at end of turn).",
        )

        feature3 = Feature(
            name="Retrieve Objective",
            uses=1,
            action=ActionType.Action,
            description=f"{stats.selfref.capitalize()} casts *Plane Shift* on itself and up to one **Incapacitated** or **Grappled** creature, which is considered willing.",
        )

        return [feature1, feature2, feature3]


class _SpellStoring(ConstructPower):
    def __init__(self):
        super().__init__(name="Spell Storing", source="SRD 5.1 Shield Guardian")

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
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

        return [feature]


BoundProtector: Power = _BoundProtector()
ConstructedGuardian: Power = _ConstructedGuardian()
ExplosiveCore: Power = _ExplosiveCore()
ImmutableForm: Power = _ImmutableForm()
ProtectivePlating: Power = _ProtectivePlating()
Retrieval: Power = _Retrieval()
Smother: Power = _Smother()
SpellStoring: Power = _SpellStoring()

ConstructPowers: List[Power] = [
    BoundProtector,
    ConstructedGuardian,
    ExplosiveCore,
    ImmutableForm,
    ProtectivePlating,
    Retrieval,
    Smother,
    SpellStoring,
]

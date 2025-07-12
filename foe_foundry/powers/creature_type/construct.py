from datetime import datetime
from math import ceil
from typing import List

from num2words import num2words

from foe_foundry.references import action_ref
from foe_foundry.utils import easy_multiple_of_five

from ...attack_template import natural as natural_attacks
from ...creature_types import CreatureType
from ...damage import Attack, AttackType, Condition, DamageType
from ...die import Die
from ...features import ActionType, Feature
from ...role_types import MonsterRole
from ...size import Size
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


class ConstructPower(PowerWithStandardScoring):
    def __init__(
        self,
        name: str,
        source: str,
        icon: str,
        power_level: float = MEDIUM_POWER,
        reference_statblock: str = "Stone Golem",
        create_date: datetime | None = None,
        **score_args,
    ):
        standard_score_args = dict(require_types=CreatureType.Construct) | score_args
        super().__init__(
            name=name,
            power_category=PowerCategory.CreatureType,
            source=source,
            power_level=power_level,
            create_date=create_date,
            icon=icon,
            theme="Construct",
            reference_statblock=reference_statblock,
            score_args=standard_score_args,
        )


class _ConstructedGuardian(ConstructPower):
    def __init__(self):
        super().__init__(
            name="Constructed Guardian",
            source="Foe Foundry",
            reference_statblock="Shield Guardian",
            icon="guarded-tower",
            create_date=datetime(2023, 11, 21),
            power_level=LOW_POWER,
            bonus_roles=MonsterRole.Defender,
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Constructed Guardian",
            action=ActionType.Feature,
            description=f"If {stats.selfref} is within 10 feet of an objective (creature, location, or object) that it was designed to guard, it has advantage on attack rolls.",
        )
        return [feature]


class _ProtectivePlating(ConstructPower):
    def __init__(self):
        super().__init__(
            name="Protective Plating",
            source="Foe Foundry",
            icon="guarded-tower",
            create_date=datetime(2023, 11, 21),
            power_level=LOW_POWER,
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
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
            name="Immutable Form",
            icon="locked-box",
            source="SRD 5.1 Stone Golem",
            power_level=RIBBON_POWER,
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
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
            icon="static-guard",
            reference_statblock="Shield Guardian",
            source="SRD 5.1 Shield Guardian",
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
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
            name="Explosive Core",
            source="Foe Foundry",
            icon="planet-core",
            bonus_damage=DamageType.Fire,
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        dmg_type = DamageType.Fire
        dmg = stats.target_value(dpr_proportion=0.8, suggested_die=Die.d6)
        dc = stats.difficulty_class_easy

        feature = Feature(
            name="Explosive Core",
            action=ActionType.Reaction,
            description=f"When {stats.selfref} is destroyed, it explodes with {dmg_type.adj} energy. Each creature within 10 feet must make a DC {dc} Dexterity saving throw, \
                taking {dmg.description} {dmg_type} damage on a failure or half on a success.",
        )

        return [feature]


class _Smother(ConstructPower):
    def __init__(self):
        super().__init__(
            name="Smother",
            reference_statblock="Rug of Smothering",
            icon="blanket",
            source="SRD 5.1 Rug of Smothering",
            attack_names={"-", natural_attacks.Slam},
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Damage Transfer",
            action=ActionType.Feature,
            description=f"While it is grappling a creature, {stats.selfref} takes only half the damage dealt to it, and the creature grappled by {stats.selfref} takes the other half.",
        )
        return [feature]

    def modify_stats_inner(self, stats: BaseStatblock) -> BaseStatblock:
        dc = stats.difficulty_class_easy
        grappled = Condition.Grappled
        restrained = Condition.Restrained
        blinded = Condition.Blinded

        def set_on_hit(attack: Attack) -> Attack:
            dmg = attack.damage.formula
            additional_description = f"On a hit, {stats.selfref} begins to smother the target. The creature is {grappled.caption} (escape DC {dc}). \
                While grappled this way, the creature is {restrained.caption}, {blinded.caption}, and suffers {dmg.description} ongoing bludgeoning damage at the start of each of its turns."
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
            source="Foe Foundry",
            power_level=HIGH_POWER,
            icon="bug-net",
            create_date=datetime(2023, 11, 21),
            require_cr=7,
            attack_names=["-", natural_attacks.Slam],
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class
        grappled = Condition.Grappled
        paralyzed = Condition.Paralyzed
        incapacitated = Condition.Incapacitated

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
                On a failure, the target is teleported onto {stats.selfref}'s back and is {grappled.caption} (escape DC {dc}) and {paralyzed.caption} for 1 minute (save ends at end of turn).",
        )

        feature3 = Feature(
            name="Retrieve Objective",
            uses=1,
            action=ActionType.Action,
            description=f"{stats.selfref.capitalize()} casts *Plane Shift* on itself and up to one {incapacitated.caption} or {grappled.caption} creature, which is considered willing.",
        )

        return [feature1, feature2, feature3]


class _SpellStoring(ConstructPower):
    def __init__(self):
        super().__init__(
            name="Spell Storing",
            icon="energy-tank",
            reference_statblock="Shield Guardian",
            source="SRD 5.1 Shield Guardian",
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
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
            replaces_multiattack=1,
            description=f"{stats.selfref.capitalize()} stores a single spell of {level_text} level or lower. {stats.selfref.capitalize()} may cast the spell using a spell save DC of {dc}. \
                When the spell is cast or a new spell is stored, any previously stored spell is lost. Some example spells include {examples}.",
        )

        return [feature]


class _Overclock(ConstructPower):
    def __init__(self):
        super().__init__(
            name="Overclock",
            source="A5E SRD Clockwork Sentinel",
            icon="clockwork",
            create_date=datetime(2023, 11, 21),
            require_attack_types=AttackType.AllMelee(),
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        dash = action_ref("Dash")
        temphp = easy_multiple_of_five(5 + 2 * stats.cr)
        feature = Feature(
            name="Overclock",
            recharge=5,
            action=ActionType.BonusAction,
            description=f"{stats.selfref.capitalize()} uses {dash} and gains {temphp} temporary hit points.",
        )
        return [feature]


class _Crush(ConstructPower):
    def __init__(self):
        super().__init__(
            name="Crush",
            source="A5E SRD Crusher",
            icon="crush",
            create_date=datetime(2023, 11, 21),
            require_size=Size.Huge,
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class
        dmg = stats.target_value(target=1.8, suggested_die=Die.d8)
        prone = Condition.Prone.caption
        feature = Feature(
            name="Crush",
            action=ActionType.Action,
            replaces_multiattack=2,
            description=f"{stats.selfref.capitalize()} moves up to its speed in a straight line. While doing so, it can attempt to enter Large or smaller creatures' spaces. \
                Right before {stats.selfref} attempts to enter a creature's space, that creature makes a DC {dc} Dexterity or Strength saving throw (the creature's choice). \
                If the creature succeeds at a Strength saving throw, {stats.selfref}'s movement ends for the turn. If the creature succeeds at a Dexterity saving throw, the creature may use its reaction, if available, to move up to half its Speed without provoking opportunity attacks. \
                The first time on {stats.selfref}'s turn that it enters a creature's space, that creature is knocked {prone} and takes {dmg.description} bludgeoning damage.",
        )
        return [feature]


BoundProtector: Power = _BoundProtector()
Crush: Power = _Crush()
ConstructedGuardian: Power = _ConstructedGuardian()
ExplosiveCore: Power = _ExplosiveCore()
ImmutableForm: Power = _ImmutableForm()
Overclock: Power = _Overclock()
ProtectivePlating: Power = _ProtectivePlating()
Retrieval: Power = _Retrieval()
Smother: Power = _Smother()
SpellStoring: Power = _SpellStoring()

ConstructPowers: List[Power] = [
    BoundProtector,
    Crush,
    ConstructedGuardian,
    ExplosiveCore,
    ImmutableForm,
    Overclock,
    ProtectivePlating,
    Retrieval,
    Smother,
    SpellStoring,
]

from typing import List, Set, Tuple, TypeVar

import numpy as np
from numpy.random import Generator

from ...attack_template import natural, spell, weapon
from ...attributes import Stats
from ...creature_types import CreatureType
from ...damage import DamageType, conditions
from ...die import Die, DieFormula
from ...features import ActionType, Feature
from ...role_types import MonsterRole
from ...size import Size
from ...statblocks import BaseStatblock
from ...utils import easy_multiple_of_five
from ..attack_modifiers import AttackModifiers, resolve_attack_modifier
from ..power import HIGH_POWER, Power, PowerBackport, PowerType
from ..utils import score


class _Dueling(PowerBackport):
    def __init__(self):
        super().__init__(name="Dueling", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return score(
            candidate,
            bonus_roles=[MonsterRole.Skirmisher, MonsterRole.Leader],
            attack_modifiers=[
                "-",
                weapon.MaceAndShield,
                weapon.SpearAndShield,
                weapon.SpearAndShield,
                weapon.JavelinAndShield,
                weapon.RapierAndShield,
            ],
        )

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, Feature | List[Feature] | None]:
        feature = Feature(
            name="Dueling Expert",
            action=ActionType.Feature,
            description=f"If {stats.selfref} makes a melee attack against a creature, then that creature can't make opportunity attacks against {stats.selfref} until the end of {stats.selfref}'s turn.",
        )
        return stats, feature


class _ExpertBrawler(PowerBackport):
    def __init__(self):
        super().__init__(name="Expert Brawler", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return score(
            candidate,
            require_types=[CreatureType.Humanoid, CreatureType.Giant],
            bonus_roles=[MonsterRole.Bruiser, MonsterRole.Controller],
            attack_modifiers={"-", natural.Slam},
        )

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, Feature | List[Feature] | None]:
        dc = stats.difficulty_class_easy
        dmg = DieFormula.target_value(0.2 * stats.attack.average_damage, force_die=Die.d4)
        feature1 = Feature(
            name="Expert Brawler Hit",
            action=ActionType.Feature,
            hidden=True,
            modifies_attack=True,
            description=f"On a hit, the target is **Grappled** (escape DC {dc})",
        )

        feature2 = Feature(
            name="Pin",
            action=ActionType.BonusAction,
            description=f"{stats.selfref.capitalize()} pins a creature it is grappling. The creature is **Restrained** while grappled in this way \
                and suffers {dmg.description} ongoing bludgeoning damage at the end of each of its turns.",
        )

        return stats, [feature1, feature2]


class _Interception(PowerBackport):
    def __init__(self):
        super().__init__(name="Interception", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return score(
            candidate,
            attack_modifiers={
                "-",
                weapon.SwordAndShield,
                weapon.SpearAndShield,
                weapon.Greataxe,
                weapon.Polearm,
                weapon.MaceAndShield,
                weapon.RapierAndShield,
                weapon.Shortswords,
            },
            require_roles=[MonsterRole.Defender, MonsterRole.Bruiser],
        )

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, Feature | List[Feature] | None]:
        distance = easy_multiple_of_five(stats.speed.fastest_speed / 2.0, min_val=5, max_val=30)
        feature = Feature(
            name="Interception",
            action=ActionType.Reaction,
            description=f"If a friendly creature within {distance} ft becomes the target of an attack, {stats.selfref} can move up to {distance} ft and intercept the attack. \
                The attack targets {stats.selfref} instead of the original target.",
        )
        return stats, feature


class _BaitAndSwitch(PowerBackport):
    def __init__(self):
        super().__init__(name="Bait and Switch", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return score(
            candidate,
            require_types=CreatureType.Humanoid,
            require_roles=[
                MonsterRole.Defender,
                MonsterRole.Skirmisher,
                MonsterRole.Leader,
                MonsterRole.Bruiser,
            ],
        )

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, Feature | List[Feature] | None]:
        bonus = stats.attributes.primary_mod
        feature = Feature(
            name="Bait and Switch",
            action=ActionType.BonusAction,
            uses=1,
            description=f"{stats.selfref.capitalize()} switches places with a friendly creature within 5 feet. \
                Until the end of its next turn, the friendly creature gains a +{bonus} bonus to its AC.",
        )
        return stats, feature


class _ThrownWeaponExpert(PowerBackport):
    def __init__(self):
        super().__init__(name="Thrown Weapon Expert", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return score(
            candidate,
            attack_modifiers={
                "-",
                weapon.JavelinAndShield,
                weapon.Daggers,
            },
        )

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, Feature | List[Feature] | None]:
        attack = stats.attack.name
        feature = Feature(
            name="Quick Toss",
            action=ActionType.BonusAction,
            uses=1,
            description=f"{stats.selfref.capitalize()} makes a {attack} attack as a bonus action",
        )
        return stats, feature


class _ArmorMaster(PowerBackport):
    def __init__(self):
        super().__init__(name="Armor Master", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        def is_heavily_armored(b: BaseStatblock) -> bool:
            return any([c for c in b.ac_templates if c.is_heavily_armored])

        return score(candidate, require_callback=is_heavily_armored)

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, Feature | List[Feature] | None]:
        feature = Feature(
            name="Heavy Armor Master",
            action=ActionType.Feature,
            description=f"{stats.selfref.capitalize()} reduces the amount of bludgeoning, piercing, and slashing damage it receives by 3.",
        )
        return stats, feature


class _ShieldMaster(PowerBackport):
    def __init__(self):
        super().__init__(name="Shield Master", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return score(candidate, require_shield=True)

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, Feature | List[Feature] | None]:
        dc = stats.difficulty_class
        feature = Feature(
            name="Shield Slam",
            action=ActionType.BonusAction,
            description=f"{stats.selfref.capitalize()} shoves a creature within 5 feet. It must make a DC {dc} Strength save or be pushed up to 5 feet and fall **Prone**.",
        )
        return stats, feature


class _PolearmMaster(PowerBackport):
    def __init__(self):
        super().__init__(name="Polearm Master", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return score(candidate, attack_modifiers={"-", weapon.Polearm})

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, Feature | List[Feature] | None]:
        feature = Feature(
            name="Polearm Master",
            action=ActionType.Reaction,
            description=f"Whenever a hostile creature enters {stats.selfref.capitalize()}'s reach, it may make an attack of opportunity against that creature.",
        )
        return stats, feature


class _GreatWeaponFighting(PowerBackport):
    def __init__(self):
        super().__init__(
            name="Great Weapon Fighting", power_type=PowerType.Theme, power_level=HIGH_POWER
        )

    def score(self, candidate: BaseStatblock) -> float:
        return score(
            candidate,
            attack_modifiers={
                "-",
                weapon.Polearm,
                weapon.Greataxe,
                weapon.Greatsword,
                weapon.Maul,
            },
        )

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, Feature | List[Feature] | None]:
        dc = stats.difficulty_class
        dmg = DieFormula.target_value(1.7 * stats.attack.average_damage, force_die=Die.d12)
        dmg_type = stats.attack.damage.damage_type
        feature = Feature(
            name="Overpowering Strike",
            action=ActionType.Action,
            replaces_multiattack=2,
            recharge=5,
            description=f"{stats.selfref.capitalize()} makes an overpowering strike against a creature within 5 feet. The target must make a DC {dc} Strength saving throw. \
                On a failure, it takes {dmg.description} {dmg_type} damage and is knocked **Prone**. On a success, it instead takes half damage.",
        )
        return stats, feature


class _TwoWeaponFighting(PowerBackport):
    def __init__(self):
        super().__init__(name="Two Weapon Fighting", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return score(
            candidate,
            attack_modifiers={
                "-",
                weapon.Daggers,
                weapon.Shortswords,
            },
        )

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, Feature | List[Feature] | None]:
        dc = stats.difficulty_class

        dmg = DieFormula.target_value(stats.attack.average_damage, force_die=Die.d6)
        # make sure that the damage formula is even so the bleeding can be half
        if dmg.n_die % 2 == 1:
            dmg = DieFormula.from_dice(mod=dmg.mod or 0, d6=dmg.n_die + 1)

        bleed_dmg = DieFormula.from_dice(d6=dmg.n_die // 2)
        bleeding = conditions.Bleeding(damage=bleed_dmg)

        dmg_type = stats.attack.damage.damage_type
        feature = Feature(
            name="Whirlwind of Steel",
            action=ActionType.Action,
            replaces_multiattack=2,
            recharge=5,
            description=f"{stats.selfref.capitalize()} makes a lightning-fast flurry of strikes at a creature within 5 feet. The target must make a DC {dc} Dexterity saving throw. \
                On a failure, it takes {dmg.description} {dmg_type} damage and is {bleeding.description}. On a success, it instead takes half damage. {bleeding.description_3rd}",
        )
        return stats, feature


class _Sharpshooter(PowerBackport):
    def __init__(self):
        super().__init__(
            name="Sharpshooter", power_type=PowerType.Theme, power_level=HIGH_POWER
        )

    def score(self, candidate: BaseStatblock) -> float:
        return score(
            candidate,
            require_roles=MonsterRole.Artillery,
            attack_modifiers={
                "-",
                weapon.Longbow,
                weapon.Shortbow,
                weapon.Crossbow,
            },
        )

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, Feature | List[Feature] | None]:
        dc = stats.difficulty_class
        distance = stats.attack.range_max or stats.attack.range
        dmg = DieFormula.target_value(1.5 * stats.attack.average_damage)
        dmg_type = stats.attack.damage.damage_type
        dazed = conditions.Dazed()
        feature = Feature(
            name="Sharpshooter's Shot",
            action=ActionType.Action,
            replaces_multiattack=2,
            recharge=5,
            description=f"{stats.selfref.capitalize()} fires a deadly shot at a creature it can see within {distance} ft. The target must make a DC {dc} Dexterity saving throw. \
                On a failure, it takes {dmg.description} {dmg_type} damage and is {dazed.caption} until the end of its next turn. {dazed.description_3rd}",
        )
        return stats, feature


ArmorMaster: Power = _ArmorMaster()
BaitAndSwitch: Power = _BaitAndSwitch()
Dueling: Power = _Dueling()
ExpertBrawler: Power = _ExpertBrawler()
GreatWeaponFighting: Power = _GreatWeaponFighting()
Interception: Power = _Interception()
PolearmMaster: Power = _PolearmMaster()
Sharpshooter: Power = _Sharpshooter()
ShieldMaster: Power = _ShieldMaster()
ThrownWeaponExpert: Power = _ThrownWeaponExpert()
TwoWeaponFighting: Power = _TwoWeaponFighting()

FightingStylePowers: List[Power] = [
    ArmorMaster,
    BaitAndSwitch,
    Dueling,
    ExpertBrawler,
    GreatWeaponFighting,
    Interception,
    PolearmMaster,
    Sharpshooter,
    ShieldMaster,
    ThrownWeaponExpert,
]

from typing import List, Set, Tuple

import numpy as np
from numpy.random import Generator

from ...attack_template import natural, spell, weapon
from ...attributes import Stats
from ...damage import DamageType, conditions
from ...die import Die, DieFormula
from ...features import ActionType, Feature
from ...role_types import MonsterRole
from ...size import Size
from ...statblocks import BaseStatblock
from ...utils import easy_multiple_of_five
from ..attack import flavorful_damage_types
from ..attack_modifiers import AttackModifiers, resolve_attack_modifier
from ..power import Power, PowerType
from ..scores import HIGH_AFFINITY, LOW_AFFINITY, MODERATE_AFFINITY, NO_AFFINITY
from .organized import _score_could_be_organized


def has_training(candidate: BaseStatblock) -> bool:
    return _score_could_be_organized(candidate) >= 0


def score(
    candidate: BaseStatblock,
    target_roles: MonsterRole | Set[MonsterRole] | List[MonsterRole] | None = None,
    attack_modifiers: AttackModifiers = None,
    require_training: bool = True,
    require_living: bool = False,
) -> float:
    def clean_set(a):
        if a is None:
            return set()
        elif isinstance(a, list):
            return set(a)
        elif isinstance(a, set):
            return a
        else:
            return {a}

    target_roles = clean_set(target_roles)

    # these abilities require training and discipline
    if require_training and not has_training(candidate):
        return NO_AFFINITY

    if require_living and not candidate.creature_type.is_living:
        return NO_AFFINITY

    score = resolve_attack_modifier(candidate, attack_modifiers)

    if attack_modifiers is not None and score == 0:
        return NO_AFFINITY

    if candidate.role in target_roles:
        score += HIGH_AFFINITY

    return score


class _Dueling(Power):
    def __init__(self):
        super().__init__(name="Dueling", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return score(
            candidate,
            target_roles=[MonsterRole.Skirmisher, MonsterRole.Leader],
            attack_modifiers=[
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


class _ExpertBrawler(Power):
    def __init__(self):
        super().__init__(name="Expert Brawler", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return score(
            candidate,
            target_roles=[MonsterRole.Bruiser, MonsterRole.Controller],
            attack_modifiers=natural.Slam,
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


class _Interception(Power):
    def __init__(self):
        super().__init__(name="Interception", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return score(
            candidate,
            target_roles=[MonsterRole.Defender],
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


class _BaitAndSwitch(Power):
    def __init__(self):
        super().__init__(name="Bait and Switch", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return score(
            candidate,
            target_roles=[
                MonsterRole.Defender,
                MonsterRole.Skirmisher,
                MonsterRole.Leader,
                MonsterRole.Bruiser,
            ],
        )

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, Feature | List[Feature] | None]:
        bonus = stats.attributes.primary_attribute_score
        feature = Feature(
            name="Bait and Switch",
            action=ActionType.BonusAction,
            description=f"{stats.selfref.capitalize()} switches places with a friendly creature within 5 feet. \
                Until the end of its next turn, the friendly creature gains a +{bonus} bonus to its AC.",
        )
        return stats, feature


class _BlessedWarrior(Power):
    def __init__(self):
        super().__init__(name="Blessed Warrior", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return score(
            candidate,
            require_living=True,
            attack_modifiers=[
                weapon.SwordAndShield,
                weapon.MaceAndShield,
                weapon.Maul,
                weapon.Greatsword,
                spell.HolyBolt,
            ],
        )

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, Feature | List[Feature] | None]:
        stats = stats.scale({Stats.CHA: Stats.CHA.Boost(1), Stats.WIS: Stats.WIS.Boost(1)})
        if stats.secondary_damage_type is None:
            stats = stats.copy(secondary_damage_type=DamageType.Radiant)

        damage = DieFormula.target_value(0.5 * stats.attack.average_damage, force_die=Die.d6)
        dc = stats.difficulty_class
        feature = Feature(
            name="Word of Radiance",
            action=ActionType.Action,
            replaces_multiattack=1,
            description=f"{stats.selfref.capitalize()} utters a divine word and it shines with burning radiance. \
                Each hostile creature within 10 feet must make a DC {dc} Constitution saving throw or take {damage.description} radiant damage.",
        )
        return stats, feature


class _DruidicWarrior(Power):
    def __init__(self):
        super().__init__(name="Druidic Warrior", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return score(
            candidate,
            require_living=True,
            target_roles=[MonsterRole.Leader, MonsterRole.Controller, MonsterRole.Skirmisher],
            attack_modifiers=[weapon.Staff, weapon.Longbow, weapon.Shortbow, spell.Poisonbolt],
        )

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, Feature | List[Feature] | None]:
        stats = stats.scale({Stats.WIS: Stats.WIS.Boost(2)})
        if stats.secondary_damage_type is None:
            stats = stats.copy(secondary_damage_type=DamageType.Poison)

        healing = DieFormula.target_value(0.5 * stats.attack.average_damage, force_die=Die.d4)
        uses = stats.attributes.stat_mod(Stats.WIS)

        feature = Feature(
            name="Healing Word",
            action=ActionType.BonusAction,
            uses=uses,
            description=f"{stats.selfref.capitalize()} utters a word of primal encouragement to a friendly ally it can see within 60 feet. \
                The ally regains {healing.description} hitpoints.",
        )
        return stats, feature


class _ThrownWeaponExpert(Power):
    def __init__(self):
        super().__init__(name="Thrown Weapon Expert", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return score(
            candidate,
            attack_modifiers=[weapon.JavelinAndShield, weapon.Daggers],
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


class _ArmorMaster(Power):
    def __init__(self):
        super().__init__(name="Thrown Weapon Expert", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        organized = has_training(candidate)
        armored = any([c for c in candidate.ac_templates if c.is_armored])
        if organized and armored:
            return HIGH_AFFINITY
        else:
            return NO_AFFINITY

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, Feature | List[Feature] | None]:
        feature = Feature(
            name="Armor Master",
            action=ActionType.Feature,
            description=f"{stats.selfref.capitalize()} reduces the amount of bludgeoning, piercing, and slashing damage it receives by 3.",
        )
        return stats, feature


class _ShieldMaster(Power):
    def __init__(self):
        super().__init__(name="Shield Master", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        organized = has_training(candidate)
        if organized and candidate.uses_shield:
            return HIGH_AFFINITY
        else:
            return NO_AFFINITY

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, Feature | List[Feature] | None]:
        feature = Feature(
            name="Shield Slam",
            action=ActionType.BonusAction,
            description=f"{stats.selfref.capitalize()} uses the Shove action as a bonus action.",
        )
        return stats, feature


class _PolearmMaster(Power):
    def __init__(self):
        super().__init__(name="Polearm Master", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return score(candidate, attack_modifiers=weapon.Polearm)

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, Feature | List[Feature] | None]:
        feature = Feature(
            name="Polearm Master",
            action=ActionType.Reaction,
            description=f"Whenever a hostile creature enters {stats.selfref.capitalize()}'s reach, it may make an attack of opportunity against that creature.",
        )
        return stats, feature


class _GreatWeaponFighting(Power):
    def __init__(self):
        super().__init__(name="Great Weapon Fighting", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return score(
            candidate,
            attack_modifiers=[weapon.Polearm, weapon.Greataxe, weapon.Greatsword, weapon.Maul],
        )

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, Feature | List[Feature] | None]:
        dc = stats.difficulty_class
        dmg = DieFormula.target_value(1.5 * stats.attack.average_damage, force_die=Die.d12)
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


class _TwoWeaponFighting(Power):
    def __init__(self):
        super().__init__(name="Two Weapon Fighting", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return score(
            candidate,
            attack_modifiers=[weapon.Daggers, weapon.Shortswords],
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


class _Sharpshooter(Power):
    def __init__(self):
        super().__init__(name="Sharpshooter", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return score(
            candidate,
            target_roles=MonsterRole.Artillery,
            attack_modifiers=[weapon.Longbow, weapon.Shortbow, weapon.Crossbow],
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
BlessedWarrior: Power = _BlessedWarrior()
DruidicWarrior: Power = _DruidicWarrior()
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
    BlessedWarrior,
    DruidicWarrior,
    Dueling,
    ExpertBrawler,
    GreatWeaponFighting,
    Interception,
    PolearmMaster,
    Sharpshooter,
    ShieldMaster,
    ThrownWeaponExpert,
]

from math import ceil
from typing import Dict, List, Tuple

import numpy as np

from ...attack_template import natural as natural_attacks
from ...attack_template import weapon
from ...attributes import Skills, Stats
from ...creature_types import CreatureType
from ...damage import Attack, AttackType, Bleeding, DamageType
from ...die import Die, DieFormula
from ...features import ActionType, Feature
from ...powers import PowerType
from ...role_types import MonsterRole
from ...size import Size
from ...statblocks import BaseStatblock, MonsterDials
from ...utils import easy_multiple_of_five
from ..power import HIGH_POWER, Power, PowerBackport, PowerType
from ..scoring import AttackNames, score


def _score_bruiser(
    candidate: BaseStatblock,
    size_boost: bool = False,
    attack_names: AttackNames = None,
    **kwargs,
) -> float:
    return score(
        candidate=candidate,
        require_roles=MonsterRole.Bruiser,
        bonus_size=Size.Large if size_boost else None,
        attack_names=attack_names,
        **kwargs,
    )


class _Sentinel(PowerBackport):
    def __init__(self):
        super().__init__(name="Sentinel", power_type=PowerType.Role)

    def score(self, candidate: BaseStatblock) -> float:
        return _score_bruiser(
            candidate,
            size_boost=True,
            attack_names=[
                weapon.Polearm,
                weapon.SpearAndShield,
            ],
        )

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature]:
        feature = Feature(
            name="Sentinel",
            action=ActionType.Reaction,
            description=f"If another target moves while within {stats.roleref}'s reach then {stats.roleref} may make an attack against that target.",
        )

        return stats, feature


class _Grappler(PowerBackport):
    def __init__(self):
        super().__init__(name="Grappler", power_type=PowerType.Role)

    def score(self, candidate: BaseStatblock) -> float:
        return _score_bruiser(candidate, attack_names={"-", natural_attacks.Slam})

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature | None]:
        new_attrs = stats.attributes.grant_proficiency_or_expertise(Skills.Athletics)
        stats = stats.copy(attributes=new_attrs, primary_damage_type=DamageType.Bludgeoning)

        dc = stats.difficulty_class

        stats = stats.add_attack(
            scalar=0.7,
            damage_type=DamageType.Bludgeoning,
            attack_type=AttackType.MeleeNatural,
            die=Die.d6,
            name="Grappling Strike",
            additional_description=f"On a hit, the target must make a DC {dc} Strength save or be **Grappled** (escape DC {dc}). \
                 While grappled in this way, the creature is also **Restrained**",
        )
        return stats, None


class _Cleaver(PowerBackport):
    def __init__(self):
        super().__init__(name="Cleaver", power_type=PowerType.Role)

    def score(self, candidate: BaseStatblock) -> float:
        return _score_bruiser(
            candidate, attack_names={"-", weapon.Greataxe, natural_attacks.Claw}
        )

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature]:
        stats = stats.copy(primary_damage_type=DamageType.Slashing)

        feature = Feature(
            name="Cleaving Blows",
            action=ActionType.BonusAction,
            description=f"Immediately after the {stats.selfref} hits with a weapon attack, it may make the same attack against another target within its reach.",
            recharge=4,
        )

        return stats, feature


class _StunningBlow(PowerBackport):
    def __init__(self):
        super().__init__(
            name="Stunning Blow", power_type=PowerType.Role, power_level=HIGH_POWER
        )

    def score(self, candidate: BaseStatblock) -> float:
        return _score_bruiser(
            candidate,
            require_damage=DamageType.Bludgeoning,
            attack_names={weapon.Maul, weapon.MaceAndShield, natural_attacks.Slam},
        )

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature]:
        stats = stats.copy(primary_damage_type=DamageType.Bludgeoning)

        dc = stats.difficulty_class

        feature = Feature(
            name="Stunning Blow",
            action=ActionType.BonusAction,
            description=f"Immediately after the {stats.roleref} hits with a weapon attack, it may force the target to succeed on a DC {dc} Constitution save or be **Stunned** until the end of the {stats.selfref}'s next turn.",
            recharge=6,
        )

        return stats, feature


class _Disembowler(PowerBackport):
    def __init__(self):
        super().__init__(name="Disembowler", power_type=PowerType.Role)

    def score(self, candidate: BaseStatblock) -> float:
        return _score_bruiser(
            candidate,
            require_damage=DamageType.Piercing,
            attack_names={
                natural_attacks.Bite,
                natural_attacks.Horns,
                weapon.Daggers,
            },
        )

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, List[Feature]]:
        dc = stats.difficulty_class
        attack_type = (
            AttackType.MeleeWeapon
            if stats.attack.attack_type != AttackType.MeleeNatural
            else AttackType.MeleeNatural
        )

        def customize(a: Attack) -> Attack:
            dmg = a.damage.formula.copy(mod=0)
            bleeding = Bleeding(damage=dmg)
            return a.copy(
                additional_description=f"On a hit, the target must succeed on a DC {dc} Constitution saving throw or gain {bleeding}",
            )

        stats = stats.add_attack(
            scalar=0.7,
            damage_type=DamageType.Piercing,
            attack_type=attack_type,
            name="Rend",
            callback=customize,
        )

        return stats, []


Sentinel: Power = _Sentinel()
Grappler: Power = _Grappler()
Cleaver: Power = _Cleaver()
StunningBlow: Power = _StunningBlow()
Disembowler: Power = _Disembowler()

BruiserPowers: List[Power] = [Sentinel, Grappler, Cleaver, StunningBlow, Disembowler]

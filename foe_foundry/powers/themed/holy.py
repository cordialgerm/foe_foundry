from typing import List, Set, Tuple

import numpy as np
from numpy.random import Generator

from foe_foundry.features import Feature
from foe_foundry.statblocks import BaseStatblock

from ...attack_template import natural, spell, weapon
from ...attributes import Stats
from ...creature_types import CreatureType
from ...damage import DamageType, conditions
from ...die import Die, DieFormula
from ...features import ActionType, Feature
from ...role_types import MonsterRole
from ...statblocks import BaseStatblock
from ..power import Power, PowerBackport, PowerType
from ..utils import score


def score_holy(candidate: BaseStatblock, **kwargs) -> float:
    args: dict = dict(
        candidate=candidate,
        require_stats=Stats.WIS,
        require_types=CreatureType.Humanoid,
        require_damage=DamageType.Radiant,
        bonus_roles=MonsterRole.Leader,
    )
    args.update(kwargs)
    return score(**args)


class _DivineSmite(PowerBackport):
    def __init__(self):
        super().__init__(name="Divine Smite", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return score_holy(
            candidate,
            attack_modifiers=[weapon.MaceAndShield, weapon.Greatsword, weapon.SwordAndShield],
        )

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, Feature | List[Feature] | None]:
        dc = stats.difficulty_class
        dmg = DieFormula.target_value(0.4 * stats.attack.average_damage, force_die=Die.d10)
        burning = conditions.Burning(dmg)
        feature = Feature(
            name="Divine Smite",
            action=ActionType.BonusAction,
            recharge=5,
            description=f"Immediately after hitting a target, {stats.roleref} forces the target to make a DC {dc} Constitution saving throw. On a failure, the target is {burning}",
        )

        return stats, feature


class _MassCureWounds(PowerBackport):
    def __init__(self):
        super().__init__(name="Mass Cure Wounds", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return score_holy(candidate)

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, Feature | List[Feature] | None]:
        feature = Feature(
            name="Mass Cure Wounds",
            action=ActionType.Action,
            uses=1,
            replaces_multiattack=2,
            description=f"{stats.roleref.capitalize()} casts *Mass Cure Wounds*",
        )

        return stats, feature


class _WordOfRadiance(PowerBackport):
    def __init__(self):
        super().__init__(name="Word of Radiance", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return score_holy(candidate)

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, Feature | List[Feature] | None]:
        damage = DieFormula.target_value(0.6 * stats.attack.average_damage, force_die=Die.d6)
        dc = stats.difficulty_class

        feature = Feature(
            name="Word of Radiance",
            action=ActionType.Action,
            replaces_multiattack=1,
            description=f"{stats.roleref.capitalize()} utters a divine word and it shines with burning radiance. \
                Each hostile creature within 10 feet must make a DC {dc} Constitution saving throw or take {damage.description} radiant damage.",
        )

        return stats, feature


DivineSmite: Power = _DivineSmite()
MassCureWounds: Power = _MassCureWounds()
WordOfRadiance: Power = _WordOfRadiance()

HolyPowers: List[Power] = [DivineSmite, MassCureWounds, WordOfRadiance]

from typing import List, Tuple

import numpy as np

from foe_foundry.features import Feature
from foe_foundry.powers.power_type import PowerType
from foe_foundry.statblocks import BaseStatblock

from ...attributes import Skills, Stats
from ...creature_types import CreatureType
from ...damage import AttackType, DamageType
from ...features import ActionType, Feature
from ...role_types import MonsterRole
from ...statblocks import BaseStatblock, MonsterDials
from ..power import Power, PowerType
from ..scores import (
    EXTRA_HIGH_AFFINITY,
    HIGH_AFFINITY,
    LOW_AFFINITY,
    MODERATE_AFFINITY,
    NO_AFFINITY,
)


class _NimbleReaction(Power):
    def __init__(self):
        super().__init__(name="Nimble Reaction", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        score = 0

        if candidate.primary_attribute == Stats.DEX:
            score += LOW_AFFINITY

        if candidate.attributes.has_proficiency_or_expertise(Skills.Acrobatics):
            score += HIGH_AFFINITY

        if candidate.speed.fastest_speed >= 40:
            score += MODERATE_AFFINITY

        return score if score > 0 else NO_AFFINITY

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature]:
        new_attrs = stats.attributes.grant_proficiency_or_expertise(Skills.Acrobatics)
        stats = stats.copy(attributes=new_attrs)

        feature = Feature(
            name="Nimble Reaction",
            action=ActionType.Reaction,
            description=f"When {stats.selfref} is the only target of a melee attack, they can move up to their speed without provoking opportunity attacks.\
                If this movement leaves {stats.selfref} outside the attacking creature's reach, then the attack misses.",
            recharge=4,
        )

        return stats, feature


class _Impersonation(Power):
    def __init__(self):
        super().__init__(name="Impersonation", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        creature_types = {
            CreatureType.Fey: HIGH_AFFINITY,
            CreatureType.Fiend: MODERATE_AFFINITY,
            CreatureType.Aberration: MODERATE_AFFINITY,
            CreatureType.Ooze: MODERATE_AFFINITY,
            CreatureType.Humanoid: MODERATE_AFFINITY,
        }

        roles = {MonsterRole.Ambusher: LOW_AFFINITY, MonsterRole.Controller: LOW_AFFINITY}

        score = creature_types.get(candidate.creature_type, 0) + roles.get(candidate.role, 0)
        return score if score > 0 else NO_AFFINITY

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature]:
        # this creature should be tricky
        new_attrs = stats.attributes.grant_proficiency_or_expertise(Skills.Deception).boost(
            Stats.CHA, 2
        )
        stats = stats.copy(attributes=new_attrs)

        # if this is a humanoid, it should be an illusionist spellcaster
        if stats.creature_type == CreatureType.Humanoid:
            stats = stats.copy(
                attack_type=AttackType.RangedSpell, secondary_damage_type=DamageType.Psychic
            )

        dc = 8 + stats.attributes.stat_mod(Stats.CHA) + stats.attributes.proficiency

        feature = Feature(
            name="Impersonation",
            action=ActionType.BonusAction,
            recharge=6,
            description=f"Until the start of their next turn, {stats.selfref} changes their appearance to look exactly like another creature who is within 5 feet of them \
                    and is no more than one size smaller or larger. Other creatures must make a DC {dc} Perception check each time they make an attack against {stats.selfref} or the impersonated creature. \
                    On a failure, the attack is made against the wrong target, without the attacker knowing.",
        )

        return stats, feature


NimbleReaction: Power = _NimbleReaction()
Impersonation: Power = _Impersonation()

TrickyPowers: List[Power] = [NimbleReaction, Impersonation]

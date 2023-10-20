from typing import List, Tuple

from numpy.random import Generator

from ...creature_types import CreatureType
from ...damage import AttackType
from ...features import ActionType, Feature
from ...role_types import MonsterRole
from ...size import Size
from ...skills import Skills, Stats
from ...statblocks import BaseStatblock
from ..power import LOW_POWER, Power, PowerBackport, PowerType
from ..scoring import score


def score_defender(candidate: BaseStatblock, **kwargs) -> float:
    return score(
        candidate=candidate,
        require_roles=MonsterRole.Defender,
        bonus_skills=Skills.Intimidation,
        bonus_shield=True,
        bonus_attack_types=AttackType.AllMelee(),
        **kwargs,
    )


class _Defender(PowerBackport):
    """When an ally within 5 feet of this creature is targeted by an attack or spell, this creature can make themself the intended target of the attack."""

    def __init__(self):
        super().__init__(name="Defender", power_type=PowerType.Role, power_level=LOW_POWER)

    def score(self, candidate: BaseStatblock) -> float:
        return score_defender(candidate)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        name = "Defender"

        feature = Feature(
            name=name,
            description=f"When an ally within 5 feet is targeted by an attack or spell, {stats.selfref} can make themselves the intended target of the attack or spell instead.",
            action=ActionType.Reaction,
        )
        return stats, feature


class _StickWithMe(PowerBackport):
    def __init__(self):
        super().__init__(name="Stick with Me!", power_type=PowerType.Role)

    def score(self, candidate: BaseStatblock) -> float:
        return score_defender(candidate)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        feature = Feature(
            name="Stick with Me!",
            description=f"On a hit, the target has disadvantage on attack rolls against any other creature until the end of its next turn.",
            action=ActionType.Feature,
            hidden=True,
            modifies_attack=True,
        )
        return stats, feature


class _Blocker(PowerBackport):
    def __init__(self):
        super().__init__(name="Blocker", power_type=PowerType.Role, power_level=LOW_POWER)

    def score(self, candidate: BaseStatblock) -> float:
        return score_defender(candidate, bonus_size=Size.Large)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        new_attrs = stats.attributes.grant_proficiency_or_expertise(Skills.Athletics)
        stats = stats.copy(attributes=new_attrs)

        feature = Feature(
            name="Blocker",
            description=f"Any creature starting their turn next to {stats.selfref} has their speed reduced by half until the end of their turn.",
            action=ActionType.Feature,
        )

        return stats, feature


class _SpellReflection(PowerBackport):
    def __init__(self):
        super().__init__(name="Blocker", power_type=PowerType.Role)

    def score(self, candidate: BaseStatblock) -> float:
        return score_defender(
            candidate,
            require_types={
                CreatureType.Aberration,
                CreatureType.Dragon,
                CreatureType.Fiend,
                CreatureType.Monstrosity,
            },
        )

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        feature = Feature(
            name="Spell Reflection",
            action=ActionType.Reaction,
            description=f"If {stats.selfref} succeeds on a saving throw against a spell or if a spell attack misses it, then {stats.selfref} can choose another creature (including the spellcaster) it can see within 120 feet of it. \
                The spell or attack targets the chosen creature instead.",
        )

        return stats, feature


Blocker: Power = _Blocker()
Defender: Power = _Defender()
StickWithMe: Power = _StickWithMe()
SpellReflection: Power = _SpellReflection()


DefenderPowers: List[Power] = [Blocker, Defender, StickWithMe, SpellReflection]

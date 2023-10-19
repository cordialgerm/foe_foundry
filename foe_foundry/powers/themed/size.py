from math import ceil
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
from ...size import Size
from ...statblocks import BaseStatblock, MonsterDials
from ..power import HIGH_POWER, Power, PowerBackport, PowerType
from ..utils import score


class _Gigantic(PowerBackport):
    """Increases the size and damage of the creature but lowers its AC"""

    def __init__(self):
        super().__init__(name="Gigantic", power_type=PowerType.Theme, power_level=HIGH_POWER)

    def score(self, candidate: BaseStatblock) -> float:
        return score(
            candidate=candidate,
            require_types=[
                CreatureType.Beast,
                CreatureType.Monstrosity,
                CreatureType.Construct,
            ],
            bonus_roles=[MonsterRole.Defender, MonsterRole.Bruiser],
            require_attack_types=AttackType.AllMelee(),
            require_cr=5,
        )

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature]:
        new_attrs = (
            stats.attributes.grant_save_proficiency(Stats.STR)
            .grant_proficiency_or_expertise(Skills.Athletics)
            .change_primary(Stats.STR)
        )

        stats = stats.copy(
            size=stats.size.increment(), attributes=new_attrs
        ).apply_monster_dials(dials=MonsterDials(ac_modifier=-2, attack_damage_dice_modifier=1))

        feature = Feature(
            name="Gigantic",
            action=ActionType.Feature,
            description="This creature is one size larger than its usual kin.",
        )
        return stats, feature


class _Diminutive(PowerBackport):
    """Decreases the size and damage of the creature but increases its AC"""

    def __init__(self):
        super().__init__(name="Diminutive", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        def can_be_small(candidate: BaseStatblock) -> bool:
            return candidate.size <= Size.Medium

        return score(
            candidate=candidate,
            require_types=[CreatureType.Humanoid, CreatureType.Fey],
            require_callback=can_be_small,
            bonus_roles={
                MonsterRole.Ambusher,
                MonsterRole.Controller,
                MonsterRole.Skirmisher,
            },
        )

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature]:
        new_attrs = (
            stats.attributes.grant_proficiency_or_expertise(Skills.Stealth, Skills.Acrobatics)
            .grant_save_proficiency(Stats.DEX)
            .change_primary(Stats.DEX)
        )

        stats = stats.copy(
            size=stats.size.decrement(), attributes=new_attrs
        ).apply_monster_dials(dials=MonsterDials(ac_modifier=2, attack_damage_modifier=-1))

        feature = Feature(
            name="Diminutive",
            action=ActionType.Feature,
            description="This creature is one size smaller than its kin",
        )
        return stats, feature


Gigantic: Power = _Gigantic()
Diminutive: Power = _Diminutive()


SizePowers: List[Power] = [
    Diminutive,
    Gigantic,
]

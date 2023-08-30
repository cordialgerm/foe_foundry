from math import ceil, floor

import numpy as np

from foe_foundry.statblocks import BaseStatblock

from ..ac import ArmorType
from ..attributes import Skills, Stats
from ..creature_types import CreatureType
from ..damage import AttackType, Condition, DamageType
from ..size import Size, get_size_for_cr
from ..statblocks import BaseStatblock, MonsterDials
from ..utils.rng import choose_enum
from .template import CreatureTypeTemplate


class _HumanoidTemplate(CreatureTypeTemplate):
    def __init__(self):
        super().__init__(name="Humanoid", creature_type=CreatureType.Humanoid)

    def alter_base_stats(self, stats: BaseStatblock, rng: np.random.Generator) -> BaseStatblock:
        stats = stats.apply_monster_dials(MonsterDials(recommended_powers_modifier=1))

        return stats.copy(
            creature_type=CreatureType.Humanoid, size=Size.Medium, languages=["Common"]
        )


HumanoidTemplate: CreatureTypeTemplate = _HumanoidTemplate()

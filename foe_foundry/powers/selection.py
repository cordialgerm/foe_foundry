from typing import List

import numpy as np

from ..creature_types import CreatureType
from ..statblocks import BaseStatblock
from .attack import AttackPowers
from .common import CommonPowers
from .creatures.aberration import AberrationPowers
from .movement import MovementPowers
from .power import Power
from .power_type import PowerType
from .static import StaticPowers


def select_powers(
    stats: BaseStatblock, power_type: PowerType, rng: np.random.Generator, n: int = 1
) -> List[Power]:
    """Select powers based on scoring the power for the creature"""

    def select(powers: List[Power]) -> List[Power]:
        weights = np.array([p.score(stats) for p in powers])
        p = weights / np.sum(weights)
        indxs = rng.choice(a=len(powers), size=n, p=p, replace=False)
        return np.array(powers, dtype=object)[indxs].tolist()

    if power_type == PowerType.Movement:
        return select(MovementPowers)
    elif power_type == PowerType.Static:
        return select(StaticPowers)
    elif power_type == PowerType.Attack:
        return select(AttackPowers)
    elif power_type == PowerType.Common:
        return select(CommonPowers)
    elif power_type == PowerType.Creature:
        return select(_creature_powers(stats.creature_type))
    elif power_type == PowerType.Role:
        raise NotImplementedError("TODO")  # TODO


def _creature_powers(creature_type: CreatureType) -> List[Power]:
    if creature_type == CreatureType.Aberration:
        return AberrationPowers
    else:
        raise NotImplementedError("TODO")  # TODO

from typing import List, overload

import numpy as np
import numpy.typing as npt

from ..creature_types import CreatureType
from ..role_types import MonsterRole
from ..statblocks import BaseStatblock
from . import common, movement, static
from .creatures import aberration, beast, celestial, construct
from .power import Power
from .power_type import PowerType
from .roles import ambusher, artillery, bruiser, controller, defender, leader, skirmisher
from .themed import ThemedPowers, poison, tricky, warrior


def select_power(
    stats: BaseStatblock, power_type: PowerType, rng: np.random.Generator
) -> Power | None:
    powers = select_powers(stats=stats, power_type=power_type, rng=rng, n=1)
    return powers[0] if len(powers) > 0 else None


def select_powers(
    stats: BaseStatblock, power_type: PowerType, rng: np.random.Generator, n: int
) -> List[Power]:
    """Select powers based on scoring the power for the creature"""

    def select(powers: List[Power]) -> List[Power]:
        return select_from_powers(stats, powers, rng, n)

    if power_type == PowerType.Movement:
        return select(movement.MovementPowers)
    elif power_type == PowerType.Static:
        return select(static.StaticPowers)
    elif power_type == PowerType.Common:
        return select(common.CommonPowers)
    elif power_type == PowerType.Creature:
        return select(_creature_powers(stats.creature_type))
    elif power_type == PowerType.Role:
        return select(_role_powers(stats.role))
    elif power_type == PowerType.Theme:
        return select(ThemedPowers)
    else:
        raise NotImplemented(f"{power_type} powers not yet supported")


def select_from_powers(
    stats: BaseStatblock,
    powers: List[Power],
    rng: np.random.Generator,
    n: int,
    multipliers: npt.NDArray[np.float_] | None = None,
) -> List[Power]:
    weights = np.array([p.score(stats) for p in powers], dtype=float)
    if multipliers is not None:
        weights = weights * multipliers
    indxs = weights > 0
    weights[indxs] = np.exp(weights[indxs])
    weights[~indxs] = 0

    if np.sum(weights) == 0:
        return []

    p = weights / np.sum(weights)
    indxs = rng.choice(a=len(powers), size=n, p=p, replace=False)
    return np.array(powers, dtype=object)[indxs].tolist()


def _creature_powers(creature_type: CreatureType) -> List[Power]:
    if creature_type == CreatureType.Aberration:
        return aberration.AberrationPowers
    elif creature_type == CreatureType.Beast:
        return beast.BeastPowers + [common.NotDeadYet, common.GoesDownFighting]
    elif creature_type == CreatureType.Celestial:
        return celestial.CelestialPowers
    elif creature_type == CreatureType.Construct:
        return construct.ConstructPowers
    elif creature_type == CreatureType.Beast:
        return [] + [common.GoesDownFighting]  # TODO
    elif creature_type == CreatureType.Plant:
        return [] + poison.PoisonPowers
    else:
        raise NotImplementedError("TODO")  # TODO


def _role_powers(role_type: MonsterRole) -> List[Power]:
    if role_type == MonsterRole.Ambusher:
        return ambusher.AmbusherPowers + [tricky.NimbleReaction, common.Vanish]
    elif role_type == MonsterRole.Artillery:
        return artillery.ArtilleryPowers
    elif role_type == MonsterRole.Bruiser:
        return bruiser.BruiserPowers + [common.GoesDownFighting, common.Frenzy]
    elif role_type == MonsterRole.Controller:
        return controller.ControllerPowers + [warrior.PinningShot]
    elif role_type == MonsterRole.Defender:
        return defender.DefenderPowers + [warrior.Challenger, common.Defender]
    elif role_type == MonsterRole.Leader:
        return leader.LeaderPowers + [common.MarkTheTarget]
    elif role_type == MonsterRole.Skirmisher:
        return skirmisher.SkirmisherPowers + [common.Vanish, artillery.QuickStep]  # TODO
    else:
        raise ValueError(f"Unsupported monster role {role_type}")

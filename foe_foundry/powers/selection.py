from typing import List, overload

import numpy as np
import numpy.typing as npt

from ..creature_types import CreatureType
from ..role_types import MonsterRole
from ..statblocks import BaseStatblock
from . import common, movement, static
from .creatures import (
    aberration,
    beast,
    celestial,
    construct,
    dragon,
    elemental,
    fey,
    fiend,
    giant,
)
from .power import Power
from .power_type import PowerType
from .roles import ambusher, artillery, bruiser, controller, defender, leader, skirmisher
from .themed import ThemedPowers, breath, organized, poison, tricky, warrior


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

    norm_weights = np.zeros_like(weights)
    norm_weights[indxs] = weights[indxs] / np.median(weights[indxs])

    if np.sum(norm_weights) == 0:
        return []

    p = np.zeros_like(norm_weights)
    p[indxs] = np.exp(norm_weights[indxs])
    p = p / np.sum(p)
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
    elif creature_type == CreatureType.Dragon:
        return dragon.DragonPowers + breath.BreathPowers + [movement.Flyer]
    elif creature_type == CreatureType.Elemental:
        return elemental.ElementalPowers + [common.DamagingAura] + movement.MovementPowers
    elif creature_type == CreatureType.Fey:
        return fey.FeyPowers + tricky.TrickyPowers
    elif creature_type == CreatureType.Fiend:
        return fiend.FiendishPowers + [common.DelightsInSuffering]
    elif creature_type == CreatureType.Giant:
        return giant.GiantPowers + warrior.WarriorPowers
    elif creature_type == CreatureType.Plant:
        return [] + poison.PoisonPowers  # TODO
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
        return leader.LeaderPowers + [common.MarkTheTarget] + organized.OrganizedPowers
    elif role_type == MonsterRole.Skirmisher:
        return skirmisher.SkirmisherPowers + [common.Vanish, artillery.QuickStep]  # TODO
    else:
        raise ValueError(f"Unsupported monster role {role_type}")

from typing import List, overload

import numpy as np
import numpy.typing as npt

from ..creature_types import CreatureType
from ..role_types import MonsterRole
from ..statblocks import BaseStatblock
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
    ooze,
    plant,
    undead,
)
from .power import Power
from .power_type import PowerType
from .roles import ambusher, artillery, bruiser, controller, defender, leader, skirmisher
from .scores import EXTRA_HIGH_AFFINITY
from .themed import (
    ThemedPowers,
    breath,
    clever,
    cruel,
    deathly,
    flying,
    monstrous,
    organized,
    poison,
    reckless,
    sneaky,
    tough,
    tricky,
    warrior,
)


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

    if power_type == PowerType.Creature:
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
    weights[weights > EXTRA_HIGH_AFFINITY] = EXTRA_HIGH_AFFINITY
    if multipliers is not None:
        weights = weights * multipliers
    indxs = weights > 0
    n_total = int(np.sum(indxs))
    if n > n_total:
        n = n_total

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
        return beast.BeastPowers + [sneaky.NotDeadYet, tough.GoesDownFighting]
    elif creature_type == CreatureType.Celestial:
        return celestial.CelestialPowers
    elif creature_type == CreatureType.Construct:
        return construct.ConstructPowers
    elif creature_type == CreatureType.Dragon:
        return dragon.DragonPowers + breath.BreathPowers + [flying.Flyer]
    elif creature_type == CreatureType.Elemental:
        return elemental.ElementalPowers + [elemental.DamagingAura]
    elif creature_type == CreatureType.Fey:
        return fey.FeyPowers + tricky.TrickyPowers
    elif creature_type == CreatureType.Fiend:
        return fiend.FiendishPowers + [cruel.DelightsInSuffering]
    elif creature_type == CreatureType.Giant:
        return giant.GiantPowers + warrior.WarriorPowers
    elif creature_type == CreatureType.Humanoid:
        return []
    elif creature_type == CreatureType.Monstrosity:
        return monstrous.MonstrousPowers + [sneaky.NotDeadYet, tough.GoesDownFighting]
    elif creature_type == CreatureType.Ooze:
        return ooze.OozePowers + [monstrous.Swallow]
    elif creature_type == CreatureType.Plant:
        return plant.PlantPowers + poison.PoisonPowers
    elif creature_type == CreatureType.Undead:
        return undead.UndeadPowers + deathly.DeathlyPowers
    else:
        raise ValueError(f"Unsupported creature type {creature_type}")


def _role_powers(role_type: MonsterRole) -> List[Power]:
    if role_type == MonsterRole.Ambusher:
        return ambusher.AmbusherPowers + [tricky.NimbleReaction, sneaky.Vanish]
    elif role_type == MonsterRole.Artillery:
        return artillery.ArtilleryPowers
    elif role_type == MonsterRole.Bruiser:
        return bruiser.BruiserPowers + [tough.GoesDownFighting, reckless.Frenzy]
    elif role_type == MonsterRole.Controller:
        return controller.ControllerPowers
    elif role_type == MonsterRole.Defender:
        return defender.DefenderPowers + [warrior.Challenger]
    elif role_type == MonsterRole.Leader:
        return leader.LeaderPowers + [clever.MarkTheTarget] + organized.OrganizedPowers
    elif role_type == MonsterRole.Skirmisher:
        return skirmisher.SkirmisherPowers + [sneaky.Vanish, artillery.QuickStep]
    else:
        raise ValueError(f"Unsupported monster role {role_type}")

from typing import List

from ..power import Power
from . import (
    aberrant,
    bestial,
    charm,
    deathly,
    fearsome,
    monstrous,
    organized,
    poison,
    tricky,
    warrior,
)

ThemedPowers: List[Power] = (
    aberrant.AberrantPowers
    + bestial.BestialPowers
    + charm.CharmPowers
    + deathly.DeathlyPowers
    + fearsome.FearsomePowers
    + monstrous.MonstrousPowers
    + organized.OrganizedPowers
    + poison.PoisonPowers
    + tricky.TrickyPowers
    + warrior.WarriorPowers
)

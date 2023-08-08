from typing import List

from ..power import Power
from . import aberrant, bestial, charm, deathly, fearsome, organized, poison, tricky, warrior

ThemedPowers: List[Power] = (
    aberrant.AberrantPowers
    + tricky.TrickyPowers
    + warrior.WarriorPowers
    + fearsome.FearsomePowers
    + bestial.BestialPowers
    + charm.CharmPowers
    + organized.OrganizedPowers
    + deathly.DeathlyPowers
    + poison.PoisonPowers
)

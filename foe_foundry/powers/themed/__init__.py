from typing import List

from ..power import Power
from . import aberrant, bestial, charm, deathly, fearsome, organized, rogue, warrior

ThemedPowers: List[Power] = (
    aberrant.AberrantPowers
    + rogue.RoguePowers
    + warrior.WarriorPowers
    + fearsome.FearsomePowers
    + bestial.BestialPowers
    + charm.CharmPowers
    + organized.OrganizedPowers
    + deathly.DeathlyPowers
)

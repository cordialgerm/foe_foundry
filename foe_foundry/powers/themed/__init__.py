from typing import List

from ..power import Power
from . import aberrant, fearsome, rogue, warrior

ThemedPowers: List[Power] = (
    aberrant.AberrantPowers
    + rogue.RoguePowers
    + warrior.WarriorPowers
    + fearsome.FearsomePowers
)

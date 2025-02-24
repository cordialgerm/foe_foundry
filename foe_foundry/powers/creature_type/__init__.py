from typing import List

from ..power import Power
from . import (
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

CreaturePowers: List[Power] = (
    aberration.AberrationPowers
    + beast.BeastPowers
    + celestial.CelestialPowers
    + construct.ConstructPowers
    + dragon.DragonPowers
    + elemental.ElementalPowers
    + fey.FeyPowers
    + fiend.FiendishPowers
    + giant.GiantPowers
    + ooze.OozePowers
    + plant.PlantPowers
    + undead.UndeadPowers
)

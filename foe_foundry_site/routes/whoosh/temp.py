from foe_foundry.powers.creatures import (
    aberration,
    beast,
    celestial,
    construct,
    dragon,
    elemental,
    fey,
)

# TODO - add all powers
AllPowers = (
    aberration.AberrationPowers
    + beast.BeastPowers
    + celestial.CelestialPowers
    + construct.ConstructPowers
    + dragon.DragonPowers
    + elemental.ElementalPowers
    + fey.FeyPowers
)

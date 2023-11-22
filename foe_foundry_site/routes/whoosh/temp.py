from foe_foundry.powers.creatures import (
    aberration,
    beast,
    celestial,
    construct,
    dragon,
    elemental,
)

# TODO - add all powers
AllPowers = (
    aberration.AberrationPowers
    + beast.BeastPowers
    + celestial.CelestialPowers
    + construct.ConstructPowers
    + dragon.DragonPowers
    + elemental.ElementalPowers
)

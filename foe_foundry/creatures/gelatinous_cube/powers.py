from ...powers import PowerLoadout
from ...powers.creature import gelatinous_cube
from ...powers.creature_type import ooze
from ...powers.roles import ambusher

PerksTransparent = [ooze.Transparent]

PerksEngulf = [gelatinous_cube.EngulfInOoze]


PerksOozySpecialization = [
    gelatinous_cube.MetabolicSurge,
    gelatinous_cube.PerfectlyTransparent,
    ambusher.StealthySneak,
    ambusher.DeadlyAmbusher,
]

PerksAncientCube = [ooze.SlimeSpray]

LoadoutGelatinousCube = [
    PowerLoadout(
        name="Transparent",
        flavor_text="Perfectly transparent",
        powers=PerksTransparent,
        selection_count=1,
        locked=True,
    ),
    PowerLoadout(
        name="Engulf",
        flavor_text="Engulf in ooze",
        powers=PerksEngulf,
        selection_count=1,
        locked=True,
    ),
    PowerLoadout(
        name="Oozy Specialization",
        flavor_text="No two cubes are alike",
        powers=PerksOozySpecialization,
    ),
]

LoadoutAncientCube = LoadoutGelatinousCube + [
    PowerLoadout(
        name="Slime Spray",
        flavor_text="Ancient cubes can spray a corrosive slime to digest prey",
        powers=PerksAncientCube,
        selection_count=1,
        locked=True,
    ),
]

from ...powers import PowerLoadout
from ...powers.creature import nothic
from ...powers.creature_type import aberration
from ...powers.roles import controller
from ...powers.themed import anti_magic, chaotic, cursed, temporal

PerksWarpingMaddness = [nothic.WarpingMadness]

PerksMaddness = [
    aberration.GazeOfTheFarRealm,
    aberration.MadenningWhispers,
    controller.Eyebite,
    cursed.DisfiguringCurse,
    temporal.AlterFate,
    anti_magic.SpellEater,
] + nothic.NothicPowers
PerksMaddness.remove(nothic.WarpingMadness)

PerksEldritchBeacon = [chaotic.EldritchBeacon]


LoadoutHollowGazer = [
    PowerLoadout(
        name="Warping Maddness",
        flavor_text="The maddening gaze of the Hollow Gazer warps reality around it.",
        powers=PerksWarpingMaddness,
    ),
    PowerLoadout(
        name="Maddness",
        flavor_text="A gaze that drives creatures to the brink of insanity.",
        powers=PerksMaddness,
    ),
]

LoadoutHollowGazerOfRuin = LoadoutHollowGazer + [
    PowerLoadout(
        name="Eldritch Beacon",
        flavor_text="A beacon of chaotic energy that draws in the unwary.",
        powers=PerksEldritchBeacon,
    ),
]

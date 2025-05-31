from ...powers import PowerLoadout
from ...powers.creature import bugbear
from ...powers.roles import ambusher, skirmisher
from ...powers.themed import deathly, gadget, reckless, sneaky, technique

PerksFreakishlySkinny = [bugbear.FreakishlySkinny]

PerksStrangle = [
    reckless.Strangle,
    bugbear.Strangle,
    bugbear.SurpriseSnatch,
]

PerksAmbush = [
    bugbear.Skulk,
    sneaky.Vanish,
    ambusher.DeadlyAmbusher,
    ambusher.StealthySneak,
    bugbear.SnatchAndGrab,
]

PerksVicelikeGrip = [technique.GrapplingAttack]

PerksShadowMeld = [
    sneaky.CheapShot,
    sneaky.ExploitAdvantage,
    sneaky.SneakyStrike,
    skirmisher.HarassingRetreat,
    gadget.SmokeBomb,
]

PerksShadowstalker = [
    deathly.ShadowWalk,
]

LoadoutBugbear = [
    PowerLoadout(
        name="Freakishly Skinny",
        flavor_text="Freakishly skinny yet surprisingly strong",
        powers=PerksFreakeshlySkinny,
    ),
    PowerLoadout(
        name="Snatch 'n Grab",
        flavor_text="Expert at strangling and snatching prey",
        powers=PerksStrangle,
    ),
    PowerLoadout(
        name="Never See 'Em Coming",
        flavor_text="Ambush specialist with stealthy tactics",
        powers=PerksAmbush,
    ),
]

LoadoutBugbearBrute = LoadoutBugbear + [
    PowerLoadout(
        name="Vicelike Grip",
        flavor_text="Grip honed to perfection",
        powers=PerksVicelikeGrip,
    ),
]

LoadoutBugbearShadowstalker = LoadoutBugbear + [
    PowerLoadout(
        name="Shadowstalker",
        flavor_text="Master of stealth and shadow",
        powers=PerksShadowstalker,
    ),
    PowerLoadout(
        name="Shadow Meld",
        flavor_text="Blends into shadows with ease",
        powers=PerksShadowMeld,
    ),
]

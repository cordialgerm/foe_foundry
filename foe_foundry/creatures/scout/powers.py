from ...powers import PowerLoadout
from ...powers.roles import ambusher, artillery, leader, skirmisher
from ...powers.themed import clever, fast, gadget, poison, sneaky, technique, trap

PerksStealth = [
    ambusher.StealthySneak,
    sneaky.Vanish,
]

PerksHarassment = [
    skirmisher.HarassingRetreat,
    skirmisher.NimbleEscape,
    fast.NimbleReaction,
]

PerksArchery = [
    artillery.FocusShot,
    technique.Sharpshooter,
    technique.SlowingAttack,
    artillery.Overwatch,
    artillery.QuickDraw,
    clever.IdentifyWeaknes,
]

PerksCaptain = [leader.CommandTheTroops, leader.RallyTheTroops]

PerksTrapping = [gadget.BasicNet, trap.Snare, trap.SpikePit]

PerksLegendary = [clever.ArcaneMark, poison.ToxicPoison, poison.WeakeningPoison]

LoadoutScout = [
    PowerLoadout(
        name="Harassment",
        flavor_text="Scouts harass their enemies with ranged attacks and traps",
        powers=PerksHarassment,
    ),
    PowerLoadout(
        name="Archery",
        flavor_text="Scouts are experts at ranged combat",
        powers=PerksArchery,
        replace_with_species_powers=True,
    ),
]

LoadoutScoutCaptain = LoadoutScout + [
    PowerLoadout(
        name="Captain",
        flavor_text="Scout captains lead their troops with tactical prowess",
        powers=PerksCaptain,
    ),
]

LoadoutRanger = LoadoutScout + [
    PowerLoadout(
        name="Stealth",
        flavor_text="Rangers are experts at stealth and ambushes",
        powers=PerksStealth,
    ),
    PowerLoadout(
        name="Trapping",
        flavor_text="Rangers are experts at setting traps and snares",
        powers=PerksTrapping,
    ),
]

LoadoutFirstScout = LoadoutRanger + [
    PowerLoadout(
        name="First Captain",
        flavor_text="First scouts are elite scouts with legendary abilities",
        powers=PerksCaptain,
    )
]

from foe_foundry.powers import PowerLoadout
from foe_foundry.powers.roles import ambusher, artillery, skirmisher
from foe_foundry.powers.themed import (
    anti_ranged,
    clever,
    cruel,
    fast,
    fearsome,
    gadget,
    poison,
    technique,
)

# Cunning Action
PerksCunning = [skirmisher.CunningAction]

# Deadly Poison
PerksDeadlyPoisons = [
    poison.ToxicPoison,
    poison.WeakeningPoison,
    technique.PoisonedAttack,
]

# Fast
PerksQuick = [
    fast.Evasion,
    anti_ranged.HardToPinDown,
    fast.NimbleReaction,
    artillery.QuickDraw,
]

# Sniper
PerksAssassinate = [
    cruel.BrutalCritical,
    ambusher.DeadlyAmbusher,
    artillery.IndirectFire,
    clever.IdentifyWeaknes,
    artillery.Overwatch,
    artillery.FocusShot,
]

# Fabled Killer
PerksFabledKiller = [fearsome.DreadGaze, gadget.PoisonGrenade]


LoadoutContractKiller = [
    PowerLoadout(
        name="Cunning",
        flavor_text="Quick thinking and decisive action",
        powers=PerksCunning,
    ),
    PowerLoadout(
        name="Deadly Poison",
        flavor_text="Deadly poisons for lethal attacks",
        powers=PerksDeadlyPoisons,
    ),
    PowerLoadout(
        name="Nimble",
        flavor_text="Quick and agile",
        powers=PerksQuick,
        replace_with_species_powers=True,
    ),
]

LoadoutAssassin = LoadoutContractKiller + [
    PowerLoadout(
        name="Assassination",
        flavor_text="Deadly ambushes and precise strikes",
        powers=PerksAssassinate,
    )
]

LoadoutLegendaryAssassin = LoadoutAssassin + [
    PowerLoadout(
        name="Fabled Killer",
        flavor_text="A legendary assassin feared by all",
        powers=PerksFabledKiller,
    )
]

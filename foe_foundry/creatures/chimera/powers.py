from ...powers import PowerLoadout
from ...powers.creature import chimera
from ...powers.themed import domineering, flying, monstrous, reckless, serpentine, tough

PerksDragonsBreath = [chimera.DragonsBreath]

PerksQuarellsome = [chimera.QuarellingHeads]

# Wrathful
PerksWrathful = [
    reckless.BloodiedRage,
    monstrous.Rampage,
    monstrous.Frenzy,
    tough.JustAScratch,
    serpentine.InterruptingHiss,
]

PerksAggressive = [
    reckless.Overrun,
    reckless.Toss,
    flying.WingedCharge,
    monstrous.LingeringWound,
]

PerksSovereign = [domineering.CommandingPresence]

LoadoutChimera = [
    PowerLoadout(
        name="Quarellsome",
        flavor_text="The chimera's heads bicker and squabble, each vying for control.",
        powers=PerksQuarellsome,
    ),
    PowerLoadout(
        name="Dragons Breath",
        flavor_text="The chimera's dragon head breathes fire, scorching its enemies.",
        powers=PerksDragonsBreath,
    ),
    PowerLoadout(
        name="Wrathful",
        flavor_text="The chimera's rage is palpable, its attacks fueled by fury.",
        powers=PerksWrathful,
    ),
    PowerLoadout(
        name="Aggressive",
        flavor_text="The chimera charges into battle with reckless abandon, its attacks relentless.",
        powers=PerksAggressive,
    ),
]


LoadoutChimeraSovereign = LoadoutChimera + [
    PowerLoadout(
        name="Sovereign",
        flavor_text="The chimera sovereign commands the battlefield with an iron fist, its presence overwhelming.",
        powers=PerksSovereign,
    )
]

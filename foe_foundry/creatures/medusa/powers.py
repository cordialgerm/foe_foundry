from ...powers import PowerLoadout
from ...powers.roles import ambusher, artillery, controller, skirmisher
from ...powers.themed import (
    cursed,
    petrifying,
    poison,
    serpentine,
    technique,
)

PerksNimble = [skirmisher.NimbleEscape]
PerksPetrification = [petrifying.PetrifyingGaze]

PerksSappingAttacks = [
    technique.PoisonedAttack,
    technique.WeakeningAttack,
    technique.SlowingAttack,
]

PerksSerpentine = [
    serpentine.SerpentineHiss,
    serpentine.InterruptingHiss,
    poison.ToxicPoison,
    poison.WeakeningPoison,
    poison.PoisonousBlood,
    poison.VenemousMiasma,
]

PerksDeadlyArcher = [
    skirmisher.HarassingRetreat,
    ambusher.StealthySneak,
    artillery.FocusShot,
    artillery.Overwatch,
    artillery.SuppresingFire,
    artillery.IndirectFire,
]

PerksCursed = [
    controller.Eyebite,
    cursed.DisfiguringCurse,
    cursed.BestowCurse,
]

LoadoutMedusa = [
    PowerLoadout(
        name="Petrifying Gaze",
        flavor_text="A gaze to turn creature to stone.",
        powers=PerksPetrification,
    ),
    PowerLoadout(
        name="Nimble Escape",
        flavor_text="Slithering swifltly to safety",
        powers=PerksNimble,
    ),
    PowerLoadout(
        name="Sapping Attacks",
        flavor_text="Saps the strength of its foes.",
        powers=PerksSappingAttacks,
    ),
    PowerLoadout(
        name="Deadly Archer",
        flavor_text="Skilled archer with deadly aim.",
        powers=PerksDeadlyArcher,
    ),
]

LoadoutMedusaQueen = LoadoutMedusa.copy()
LoadoutMedusaQueen.pop(1)  # Remove Nimble Escape - no need because of Legendary Actions
LoadoutMedusaQueen.append(
    PowerLoadout(
        name="Ancient Curse",
        flavor_text="A curse that has withstood the test of time.",
        powers=PerksCursed,
    )
)

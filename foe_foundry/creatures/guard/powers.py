from ...powers import PowerLoadout
from ...powers.creature import guard
from ...powers.roles import artillery, defender, leader, soldier
from ...powers.themed import gadget, technique

PerksWatch = [guard.CallReinforcements, guard.SoundTheAlarm]

PerksMilitiaTraining = [
    guard.DefensiveFormation,
    guard.ProtectTheTarget,
    artillery.Overwatch,
    defender.Protection,
]
PerksBasicGadgets = [gadget.BasicNet, gadget.PotionOfHealing]
PerksAdvancedGadgets = [
    gadget.InfusedNet,
    gadget.LightningGrenade,
    gadget.PotionOfHealing,
]

PerksMartialTraining = [
    technique.BaitAndSwitch,
    technique.SlowingAttack,
    technique.DisarmingAttack,
    soldier.CoordinatedStrike,
    soldier.PreciseStrike,
]

PerksLord = [
    leader.CommandTheAttack,
    leader.CommandTheTroops,
    leader.InspiringCommander,
    leader.Intimidate,
]


LoadoutGuard = [
    PowerLoadout(
        name="Watchman", flavor_text="Trained to raise the alarm", powers=PerksWatch
    ),
    PowerLoadout(
        name="Ad-hoc militia training",
        flavor_text="Basic training",
        powers=PerksMilitiaTraining,
    ),
]
LoadoutSeargant = LoadoutGuard + [
    PowerLoadout(
        name="Equipment", flavor_text="Basic gadgets", powers=PerksBasicGadgets
    )
]
LoadoutCaptain = LoadoutGuard + [
    PowerLoadout(
        name="Equipment", flavor_text="Advanced gadgets", powers=PerksAdvancedGadgets
    ),
    PowerLoadout(
        name="Martial Training",
        flavor_text="Formal martial training",
        powers=PerksMartialTraining,
    ),
]
LoadoutLord = LoadoutCaptain + [
    PowerLoadout(
        name="Lord of the Watch",
        flavor_text="Respect commanded, but well-earned",
        powers=PerksLord,
    ),
]

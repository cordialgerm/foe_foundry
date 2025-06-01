from ...powers import PowerLoadout
from ...powers.roles import bruiser
from ...powers.themed import (
    bestial,
    cruel,
    fearsome,
    monstrous,
    reckless,
    technique,
)

PerksViciousAttacks = [
    bruiser.Rend,
    bruiser.CleavingBlows,
    bestial.OpportuneBite,
    cruel.BrutalCritical,
    monstrous.TearApart,
    monstrous.LingeringWound,
]
PerksTerritorial = [
    monstrous.Pounce,
    reckless.Charger,
    reckless.Overrun,
    monstrous.Frenzy,
]
PerksEnrage = [
    reckless.BloodiedRage,
    fearsome.FearsomeRoar,
    cruel.BloodiedFrenzy,
    bestial.RetributiveStrike,
    monstrous.Rampage,
]
PerksHulking = [
    technique.BleedingAttack,
    technique.ProneAttack,
    technique.PushingAttack,
    technique.GrazingAttack,
]

LoadoutOwlbearCub = [
    PowerLoadout(
        name="Vicious Attacks",
        flavor_text="Cruel claws and a deadly beak",
        powers=PerksViciousAttacks,
    )
]
LoadoutOwlbear = LoadoutOwlbearCub + [
    PowerLoadout(
        name="Territorial",
        flavor_text="Fiercely territorial and aggressive",
        powers=PerksTerritorial,
    ),
    PowerLoadout(
        name="Stubborn and Enraged",
        flavor_text="Enraged when wounded, striking back ferociously",
        powers=PerksEnrage,
    ),
]
LoadoutSavageOwlbear = LoadoutOwlbear + [
    PowerLoadout(
        name="Hulking",
        flavor_text="A hulking, savage specimen",
        powers=PerksHulking,
    ),
]

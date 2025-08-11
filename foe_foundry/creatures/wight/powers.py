from ...powers import PowerLoadout
from ...powers.creature import wight
from ...powers.creature_type import elemental, undead
from ...powers.roles import leader
from ...powers.themed import cursed, deathly, fearsome

PerksChillGrasp = [wight.HeartFreezingGrasp]
PerksAuras = [cursed.UnholyAura, elemental.ArcticChillAura]

PerksCursed = [
    cursed.RejectDivinity,
    cursed.BestowCurse,
    cursed.VoidSiphon,
    fearsome.DreadGaze,
    undead.SoulChill,
    undead.StygianBurst,
    undead.AntithesisOfLife,
]
PerksDreadlord = [
    wight.SoulChillingCommand,
    deathly.EndlessServitude,
    deathly.FleshPuppets,
    leader.CommandTheAttack,
]
PerksLegendary = [leader.FanaticFollowers]


LoadoutWight = [
    PowerLoadout(
        name="Heart Freezing Grasp",
        flavor_text="Heart frozen in fear",
        powers=PerksChillGrasp,
    ),
    PowerLoadout(
        name="Unholy Presence",
        flavor_text="Aura of unholy chill",
        powers=PerksAuras,
    ),
    PowerLoadout(
        name="Cursed Existence",
        flavor_text="A rejection of the natural order",
        powers=PerksCursed,
    ),
]

LoadoutChampion = LoadoutWight + [
    PowerLoadout(
        name="Dreadlord's Command",
        flavor_text="A chill command for shambling undead",
        powers=PerksDreadlord,
    ),
]

LoadoutLegendary = LoadoutChampion + [
    PowerLoadout(
        name="Fanatic Followers",
        flavor_text="Undead minions that follow the wight's commands",
        powers=PerksLegendary,
    ),
]

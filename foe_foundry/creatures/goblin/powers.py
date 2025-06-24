from ...powers import PowerLoadout
from ...powers.roles import ambusher, leader, skirmisher
from ...powers.spellcaster import shaman
from ...powers.themed import (
    cowardly,
    cursed,
    illusory,
    reckless,
    shamanic,
    sneaky,
    technique,
    thuggish,
    totemic,
    trap,
)

PerksNimbleEscape = [skirmisher.NimbleEscape]

PerksLickspittles = [skirmisher.HarassingRetreat] + cowardly.CowardlyPowers

PerksSneakyFighter = [
    sneaky.CheapShot,
    technique.VexingAttack,
    sneaky.ExploitAdvantage,
    ambusher.StealthySneak,
    skirmisher.HarassingRetreat,
] + trap.TrapPowers

PerksBrutishFighter = [
    reckless.BloodiedRage,
    reckless.Charger,
    reckless.RecklessFlurry,
    technique.CleavingAttack,
    technique.PushingAttack,
    technique.ProneAttack,
]

PerksShamanic = (
    [
        illusory.ReverseFortune,
        illusory.SpectralDuplicate,
        cursed.BestowCurse,
        cursed.DisfiguringCurse,
    ]
    + totemic.TotemicPowers
    + shamanic.ShamanicPowers
)

PerksLeaders = [
    leader.CommandTheAttack,
    leader.FanaticFollowers,
    leader.StayInFormation,
] + thuggish.ThuggishPowers

PerksGoblinAmbusher = [ambusher.AmbusherPower, ambusher.CunningAction]
PerksGoblinBoss = [thuggish.KickTheLickspittle]
PerksGoblinShamanAdept = [shaman.ShamanAdeptPower]
PerksGoblinShaman = [shaman.ShamanPower]

LoadoutBase = [
    PowerLoadout(
        name="Cunning",
        flavor_text="Clever and resourceful little nuisances",
        powers=PerksNimbleEscape,
    ),
]

LoadoutLickspittle = LoadoutBase + [
    PowerLoadout(
        name="Lickspittle",
        flavor_text="Cowardice and sycophancy keep them alive",
        powers=PerksLickspittles,
    ),
]

LoadoutWarrior = LoadoutBase + [
    PowerLoadout(
        name="Sneaky Fighting",
        flavor_text="A sneaky goblin is an experienced goblin",
        powers=PerksSneakyFighter,
    )
]

LoadoutBrute = LoadoutBase + [
    PowerLoadout(
        name="Brutish Fighting",
        flavor_text="Brutes are the backbone of goblin society, and they know it",
        powers=PerksBrutishFighter,
    )
]

LoadoutShamanAdept = LoadoutBase + [
    PowerLoadout(
        name="Shamanic Adept",
        flavor_text="Channels the power of mischievous gods and spirits",
        powers=PerksGoblinShamanAdept,
    )
]

LoadoutShaman = LoadoutBase + [
    PowerLoadout(
        name="Shaman",
        flavor_text="Channels the power of mischievous gods and spirits",
        powers=PerksGoblinShaman,
    ),
    PowerLoadout(
        name="Shamanic Boon",
        flavor_text="A shaman's connection to the spirit world is a powerful boon",
        powers=PerksShamanic,
    ),
]

LoadoutBoss = LoadoutBrute + [
    PowerLoadout(
        name="Kick the Lickspittle",
        flavor_text="Flogging will continue until morale improves",
        powers=PerksGoblinBoss,
    )
]

LoadoutWarchief = LoadoutBoss + [
    PowerLoadout(
        name="Warchief's Command",
        flavor_text="A warchief's command is absolute, and their followers are fanatical",
        powers=PerksLeaders,
    )
]

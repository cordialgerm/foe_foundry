from foe_foundry.powers import PowerLoadout
from foe_foundry.powers.creature import merrow
from foe_foundry.powers.creature_type import demon
from foe_foundry.powers.roles import ambusher, artillery, bruiser, leader
from foe_foundry.powers.themed import (
    anti_ranged,
    aquatic,
    cruel,
    emanation,
    fast,
    holy,
    icy,
    monstrous,
    poison,
    shamanic,
    storm,
    technique,
    thuggish,
)

PerksAmphibious = [aquatic.Amphibious]

PerksPoisonousAttacks = [technique.PoisonedAttack]

PerksMerrowAquaticAttacks = [
    merrow.KelpNets,
    merrow.AnemonePoison,
    merrow.ReelInThePrey,
]

PerksEliteFighter = [
    bruiser.Rend,
    bruiser.StunningBlow,
    ambusher.DeadlyAmbusher,
    cruel.BloodiedFrenzy,
    fast.NimbleReaction,
    monstrous.JawClamp,
]

PerksStormblessedMagic = [merrow.StormblessedMagic]
PerksStormcaller = [
    storm.StormcallersFury,
    storm.TempestSurge,
    emanation.LashingWinds,
    emanation.BitingFrost,
    icy.Blizzard,
]
PerksShamanic = [
    icy.IcyShield,
    holy.Heroism,
    shamanic.CommuneWithAir,
    shamanic.SpiritWalk,
    anti_ranged.Overchannel,
    artillery.TwinSpell,
]

PerksLordly = [leader.FanaticFollowers, thuggish.MobBoss, leader.CommandTheAttack]

PerksDemonicBlessing = [
    poison.PoisonousBlood,
    demon.BlackBlood,
    demon.EchoOfRage,
    demon.WhispersOfTheAbyss,
    demon.Desecration,
]

MerrowLoadout = [
    PowerLoadout(name="Amphibious", flavor_text="Amphibious", powers=PerksAmphibious),
    PowerLoadout(
        name="Poisonous Bite",
        flavor_text="Envenomed fangs",
        powers=PerksPoisonousAttacks,
    ),
    PowerLoadout(
        name="Harpoon",
        flavor_text="The fish becomes the fisher",
        powers=PerksMerrowAquaticAttacks,
    ),
]

MerrowBloodBlessedLoadout = MerrowLoadout + [
    PowerLoadout(
        name="Blood-Blessed Veteran",
        flavor_text="Elite warriors blessed by dark sacrifice",
        powers=PerksEliteFighter,
    )
]

MerrowStormblessedLoadout = [
    PowerLoadout(name="Amphibious", flavor_text="Amphibious", powers=PerksAmphibious),
    PowerLoadout(
        name="Stormblessed Magic",
        flavor_text="One with the magic of the storm",
        powers=PerksStormblessedMagic,
    ),
    PowerLoadout(
        name="Shaman of the Sea",
        flavor_text="Commune with the spirits of the sea",
        powers=PerksShamanic,
    ),
    PowerLoadout(
        name="Stormcaller",
        flavor_text="Call down the wrath of the storm",
        powers=PerksStormcaller,
    ),
]

MerrowAbyssalLordLoadout = MerrowBloodBlessedLoadout + [
    PowerLoadout(
        name="Lord of the Abyss",
        flavor_text="Ruler of the deep",
        powers=PerksLordly,
    ),
    PowerLoadout(
        name="Demonic Blessing",
        flavor_text="Blessed by the dark powers of the abyss",
        powers=PerksDemonicBlessing,
    ),
]

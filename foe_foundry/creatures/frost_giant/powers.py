# Stub for Frost Giant powers
from foe_foundry.powers import PowerLoadout
from foe_foundry.powers.creature import frost_giant
from foe_foundry.powers.creature_type import elemental, giant
from foe_foundry.powers.roles import bruiser, leader, soldier, support
from foe_foundry.powers.spellcaster import druidic
from foe_foundry.powers.themed import (
    emanation,
    gadget,
    honorable,
    hunter,
    icy,
    reckless,
    shamanic,
    technique,
    totemic,
)

LoadoutFrostGiant = PowerLoadout(
    name="Frost Giant Powers",
    flavor_text="Stub: Frost Giant powers will go here.",
    powers=[],
)

PerksAttack = [technique.ProneAttack, technique.PushingAttack]

PerksOffense = [
    frost_giant.AvalancheCharge,
    bruiser.CleavingBlows,
    bruiser.StunningBlow,
    giant.BigWindup,
    giant.CrushTheInsect,
    giant.Earthshaker,
]

PerksThrowStuff = [
    giant.Boulder,
    gadget.InfusedNet,
    reckless.Toss,
    giant.GrabAndGo,
]

PerksChallenger = [
    hunter.GloryOfTheHunt,
    frost_giant.ChillingChallenge,
    honorable.Challenge,
]

PerksIcy = [
    icy.Hoarfrost,
    elemental.ArcticChillAura,
    frost_giant.WintersShroud,
]

PerksLeader = [leader.CommandTheAttack, leader.FanaticFollowers, soldier.ActionSurge]

PerksSpellcastingAttack = [technique.SlowingAttack, technique.FreezingAttack]


PerksShaman = [
    shamanic.SpiritWolves,
    totemic.SpiritChainsTotem,
    support.WardingBond,
    shamanic.CommuneWithLand,
]

PerksRimepriest = PerksIcy + [
    icy.Blizzard,
    icy.FrostNova,
    emanation.BitingFrost,
    emanation.LashingWinds,
]

PerksSpellcasting = [druidic.DruidicMasterPower]

LoadoutFrostGiantMelee = [
    PowerLoadout(
        name="Unrivaled Strength",
        flavor_text="Towering giants that crush their foes with brute strength",
        powers=PerksAttack,
    ),
    PowerLoadout(
        name="Unrelenting",
        flavor_text="Frost giants believe that violence is the first and last answer to any problem",
        powers=PerksOffense,
    ),
    PowerLoadout(
        name="Frozen Blood",
        flavor_text="Its very veins run with the cold of the frozen wastes",
        powers=PerksIcy,
    ),
]


LoadoutFrostGiant = LoadoutFrostGiantMelee + [
    PowerLoadout(
        name="Throw Something Big!",
        flavor_text="Anything can be a weapon if it's big enough",
        powers=PerksThrowStuff,
    ),
]

LoadoutChallenger = LoadoutFrostGiantMelee + [
    PowerLoadout(
        name="Hunter's Challenge",
        flavor_text="Frost giants relish the glory of the hunt",
        powers=PerksChallenger,
    ),
]

LoadoutShaman = [
    PowerLoadout(
        name="Arctic Bolt",
        flavor_text="Harnessing the chill of the frozen wastes",
        powers=PerksSpellcastingAttack,
    ),
    PowerLoadout(
        name="Spellcasting",
        flavor_text="Guided by the elemental spirits of the land",
        powers=PerksSpellcasting,
        locked=True,
        selection_count=1,
    ),
    PowerLoadout(
        name="Shamanic",
        flavor_text="Calling upon the spirits of the land",
        powers=PerksShaman,
    ),
    PowerLoadout(
        name="Rimepriest",
        flavor_text="Masters of the frozen winds and icy magic",
        powers=PerksRimepriest,
    ),
]

LoadoutThane = LoadoutChallenger + [
    PowerLoadout(
        name="Thane of the Frozen Wastes",
        flavor_text="A leader of frost giants, commanding respect and fear",
        powers=PerksLeader,
    )
]

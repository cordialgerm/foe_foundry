from ...powers import PowerLoadout
from ...powers.creature import vrock
from ...powers.roles import bruiser, skirmisher
from ...powers.themed import (
    diseased,
    fearsome,
    flying,
    poison,
    tough,
)

PerksMagicResistance = [tough.MagicResistance]
PerksStunningScreech = [vrock.StunningScreech]

PerksPestilence = [
    poison.PoisonousBlood,
    poison.VileVomit,
    poison.VenemousMiasma,
] + diseased.DiseasedPowers

PerksDemonicSkirmisher = [
    flying.Flyby,
    fearsome.NightmarishVisions,
    bruiser.Rend,
    skirmisher.HarassingRetreat,
]

LoadoutVrock = [
    PowerLoadout(
        name="Magic Resistance",
        flavor_text="Demonic magic resistance",
        powers=PerksMagicResistance,
    ),
    PowerLoadout(
        name="Stunning Screech",
        flavor_text="A vrock's screech can stun its enemies",
        powers=PerksStunningScreech,
    ),
    PowerLoadout(
        name="Pestilence",
        flavor_text="A vrock's blood and vomit carry disease and poison",
        powers=PerksPestilence,
    ),
    PowerLoadout(
        name="Demonic Skirmisher",
        flavor_text="A vrock's skirmishing tactics",
        powers=PerksDemonicSkirmisher,
    ),
]

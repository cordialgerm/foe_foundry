from ...powers import PowerLoadout
from ...powers.creature import basilisk
from ...powers.creature_type import beast
from ...powers.themed import (
    anti_ranged,
    bestial,
    monstrous,
    petrifying,
    poison,
    reckless,
    serpentine,
    technique,
    tough,
)

PerksPetrifying = petrifying.PetrifyingPowers

PerksMagicalNature = [
    basilisk.StoneMolt,
    basilisk.StoneEater,
    poison.PoisonousBlood,
    tough.MagicResistance,
    tough.LimitedMagicImmunity,
    anti_ranged.AdaptiveCamouflage,
    serpentine.SerpentineHiss,
]

PerksPredator = [
    bestial.RetributiveStrike,
    beast.WildInstinct,
    beast.FeedingFrenzy,
    monstrous.Frenzy,
    reckless.Charger,
    bestial.BurrowingAmbush,
    beast.BestialRampage,
    monstrous.Rampage,
    monstrous.TearApart,
    monstrous.JawClamp,
    technique.BleedingAttack,
    technique.ProneAttack,
    technique.PoisonedAttack,
]

PerksBroodmother = [basilisk.BasiliskBrood]

LoadoutBasilisk = [
    PowerLoadout(
        name="Petrification",
        flavor_text="The basilisk's petrifying gaze is its most feared weapon",
        powers=PerksPetrifying,
    ),
    PowerLoadout(
        name="Magical Nature",
        flavor_text="The basilisk's blood is infused with arcane magic",
        powers=PerksMagicalNature,
    ),
    PowerLoadout(
        name="Predator",
        flavor_text="The basilisk's jaws are deadly to its prey",
        powers=PerksPredator,
    ),
]

LoadoutBasiliskBroodmother = LoadoutBasilisk + [
    PowerLoadout(
        name="Broodmother",
        flavor_text="The broodmother jealously guards her young",
        powers=PerksBroodmother,
    )
]

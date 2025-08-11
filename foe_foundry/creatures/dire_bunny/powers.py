from ...powers import Power, PowerLoadout
from ...powers.creature import dire_bunny
from ...powers.creature_type import beast
from ...powers.roles import soldier
from ...powers.themed import bestial, diseased, monstrous, reckless


def _disease_powers() -> list[Power]:
    diseases = [diseased.FilthFever, diseased.BlindingSickness, diseased.Mindfire]
    disease_powers = [
        p
        for p in diseased.RottenGraspPowers
        if p.disease in diseases  # type: ignore
    ]
    return disease_powers


PerksDiseases = _disease_powers()

PerksLeap = [soldier.MightyLeap, monstrous.Pounce, dire_bunny.ThumpOfDread]

PerksDreadFoe = [
    dire_bunny.CursedCuteness,
    dire_bunny.BurrowingDisguise,
    bestial.OpportuneBite,
    bestial.RetributiveStrike,
    beast.FeedingFrenzy,
    beast.ScentOfWeakness,
    beast.WildInstinct,
]

PerksBunnyRage = [
    reckless.BloodiedRage,
]

LoadoutDireBunny = [
    PowerLoadout(
        name="Bunny Hop", flavor_text="Not as cute as it seems", powers=PerksLeap
    ),
    PowerLoadout(
        name="Diseased", flavor_text="Diseased and dangerous", powers=PerksDiseases
    ),
    PowerLoadout(
        name="Dread Foe",
        flavor_text="A creature of nightmares",
        powers=PerksDreadFoe,
    ),
]

LoadoutMatriarch = LoadoutDireBunny + [
    PowerLoadout(
        name="Matriarch's Fury",
        flavor_text="The wrath of a mother is not to be underestimated.",
        powers=PerksBunnyRage,
    )
]

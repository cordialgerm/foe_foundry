from ...powers import PowerLoadout
from ...powers.creature import mimic
from ...powers.creature_type import ooze
from ...powers.roles import ambusher
from ...powers.themed import (
    aberrant,
    anti_magic,
    bestial,
    breath,
    illusory,
    monstrous,
    technique,
)

PerksBase = [aberrant.Adhesive, monstrous.Swallow, technique.GrapplingAttack]


PerksMimic = [
    mimic.ComfortingFamiliarty,
    bestial.MarkTheMeal,
    mimic.MagneticAttraction,
]

PerksGreaterMimic = [
    ooze.LeechingGrasp,
    ambusher.DeadlyAmbusher,
    anti_magic.RedirectTeleport,
    mimic.InhabitArmor,
    mimic.SplinterStep,
]

PerksVaultMimic = [
    ooze.SlimeSpray,
    breath.FleshMeltingBreath,
    illusory.PhantomMirage,
    mimic.HollowHome,
]

LoadoutMimic = [
    PowerLoadout(
        name="Unusual Nature",
        flavor_text="Mimics are bizzare creatures",
        powers=PerksBase,
        locked=True,
        selection_count=3,
    ),
    PowerLoadout(
        name="Meal Time",
        flavor_text="Mimics are hungry creatures that will do anything to get a meal",
        powers=PerksMimic,
    ),
]

LoadoutGreaterMimic = LoadoutMimic + [
    PowerLoadout(
        name="Greater Mimic",
        flavor_text="Greater mimics are more powerful than regular mimics",
        powers=PerksGreaterMimic,
    )
]

LoadoutVaultMimic = LoadoutGreaterMimic + [
    PowerLoadout(
        name="Vault Mimic",
        flavor_text="Vault mimics are the most powerful of all mimics",
        powers=PerksVaultMimic,
    )
]

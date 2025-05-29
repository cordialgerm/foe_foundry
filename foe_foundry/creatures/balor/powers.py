from ...powers import PowerLoadout
from ...powers.creature import balor
from ...powers.creature_type import demon, fiend
from ...powers.roles import leader
from ...powers.themed import (
    breath,
    chaotic,
    cursed,
    deathly,
    domineering,
    fearsome,
    flying,
    reckless,
    technique,
    tough,
)

powers = set()


PerksTeleportation = [fiend.FiendishTeleportation]

# Lightning Sword
PerksLightningSword = [
    technique.ShockingAttack,
    technique.DazingAttacks,
    technique.CleavingAttack,
]

# Avatar of Rage
PerksAvatarOfRage = [
    fearsome.FearsomeRoar,
    flying.WingedCharge,
    reckless.WildCleave,
    reckless.BloodiedRage,
]

# Devastation
PerksDevastating = [
    balor.FlameWhip,
    breath.InfernoBreath,
    breath.LightningBreath,
    technique.OverpoweringStrike,
    deathly.DevourSoul,
]

# Demonic Nature
PerksDemonicNature = [
    demon.BlackBlood,
    demon.Desecration,
    demon.NightmareSpawn,
    cursed.RejectDivinity,
    cursed.VoidSiphon,
]

# Anti-Magic
PerksMagicResistance = [
    tough.MagicResistance,
]

# Demonic Legion
PerksDemonicLegion = [
    chaotic.EldritchBeacon,
    leader.FanaticFollowers,
    leader.Intimidate,
    domineering.CommandingPresence,
]

# Loadouts

LoadoutBalor = [
    PowerLoadout(
        name="Lightning Sword",
        flavor_text="Crackling blade of chaos and destruction",
        powers=PerksLightningSword,
    ),
    PowerLoadout(
        name="Avatar of Rage",
        flavor_text="Embodiment of demonic fury and destruction",
        powers=PerksAvatarOfRage,
    ),
    PowerLoadout(
        name="Avatar of Devastation",
        flavor_text="Avatar of demonic destruction and chaos",
        powers=PerksDevastating,
    ),
    PowerLoadout(
        name="Avatar of Corruption",
        flavor_text="Embodiment of demonic power and corruption",
        powers=PerksDemonicNature,
    ),
    PowerLoadout(
        name="Anti-Magic",
        flavor_text="Unnaturally resilient to magic",
        powers=PerksMagicResistance,
    ),
    PowerLoadout(
        name="Demonic Teleportation",
        flavor_text="Uncontainable",
        powers=PerksTeleportation,
    ),
]

LoadoutBalorGeneral = LoadoutBalor + [
    PowerLoadout(
        name="Demonic Legion",
        flavor_text="Leader of a demonic horde",
        powers=PerksDemonicLegion,
    ),
]

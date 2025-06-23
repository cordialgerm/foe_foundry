from ...powers import PowerLoadout
from ...powers.creature_type import construct, ooze
from ...powers.roles import bruiser, defender
from ...powers.themed import breath, icy, reckless, technique, tough

PerksConstructedNature = [construct.ImmutableForm, tough.MagicResistance]
PerksGolemBase = [
    construct.ConstructedGuardian,
    construct.ProtectivePlating,
    construct.ExplosiveCore,
    defender.Protection,
    defender.ZoneOfControl,
    defender.SpellReflection,
]
PerksAttackModifications = [
    technique.GrapplingAttack,
    technique.ProneAttack,
    technique.PushingAttack,
]
LoadoutBase = [
    PowerLoadout(
        name="Constructed Nature",
        flavor_text="The golem is an artificially created creature",
        powers=PerksConstructedNature,
        locked=True,
        selection_count=2,
    )
]

# Shield Guardian
PerksShieldGuardianBase = PerksGolemBase + [defender.Protection, construct.SpellStoring]
PerksShieldGuardianUnique = [construct.BoundProtector]
PerksShieldGuardianAttack = PerksAttackModifications.copy() + [technique.SappingAttack]

LoadoutShieldGuardian = LoadoutBase + [
    PowerLoadout(
        name="Chassis",
        flavor_text="The golem's chassis has been optimized for specific use-cases",
        powers=PerksShieldGuardianBase,
    ),
    PowerLoadout(
        name="Offensive Modifications",
        flavor_text="The golem is equipped with various offensive capabilities",
        powers=PerksShieldGuardianAttack,
    ),
    PowerLoadout(
        name="Defensive Nature",
        flavor_text="The shield guardian's core purpose is to protect its master",
        powers=PerksShieldGuardianUnique,
    ),
]

# Flesh Golem
PerksFleshGolemBase = PerksGolemBase.copy()
PerksFleshGolemBase.remove(construct.ConstructedGuardian)
PerksFleshGolemBase.remove(construct.ProtectivePlating)
PerksFleshGolemBase.remove(construct.ExplosiveCore)

PerksFleshGolemUnique = [reckless.BloodiedRage, bruiser.CleavingBlows, reckless.Charger]

PerksFleshGolemAttack = PerksAttackModifications.copy() + [technique.BleedingAttack]

LoadoutFleshGolem = LoadoutBase + [
    PowerLoadout(
        name="Chasis",
        flavor_text="The golem's chasis has been optimized for specific use-cases",
        powers=PerksFleshGolemBase,
    ),
    PowerLoadout(
        name="Vicious Claws",
        flavor_text="The golem's claws have been enhanced for brutal attacks",
        powers=PerksFleshGolemAttack,
    ),
    PowerLoadout(
        name="Reckless Nature",
        flavor_text="The flesh golem is driven by an instilled rage",
        powers=PerksFleshGolemUnique,
    ),
]

# Clay Golem
PerksClayGolemBase = PerksFleshGolemBase.copy()
PerksClayGolemAttack = PerksAttackModifications.copy()
PerksClayGolemUnique = [
    ooze.EngulfInSlime,
    ooze.LeechingGrasp,
    ooze.Quicksand,
    ooze.Split,
    ooze.SlimeSpray,
]

LoadoutClayGolem = LoadoutBase + [
    PowerLoadout(
        name="Chasis",
        flavor_text="The golem's chasis has been optimized for specific use-cases",
        powers=PerksClayGolemBase,
    ),
    PowerLoadout(
        name="Offensive Modifications",
        flavor_text="The golem is equipped with various offensive capabilities",
        powers=PerksClayGolemAttack,
    ),
    PowerLoadout(
        name="Flowing Form",
        flavor_text="The clay golem's body is malleable and can be shaped to its will",
        powers=PerksClayGolemUnique,
    ),
]

# Stone Golem
PerksStoneGolemBase = PerksGolemBase
PerksStoneGolemUnique = [construct.SpellStoring, construct.Overclock, construct.Crush]
PerksStoneGolemAttack = PerksAttackModifications.copy()

LoadoutStoneGolem = LoadoutBase + [
    PowerLoadout(
        name="Chasis",
        flavor_text="The golem's chasis has been optimized for specific use-cases",
        powers=PerksStoneGolemBase,
    ),
    PowerLoadout(
        name="Offensive Modifications",
        flavor_text="The golem is equipped with various offensive capabilities",
        powers=PerksStoneGolemAttack,
    ),
    PowerLoadout(
        name="Enchanted Stone",
        flavor_text="The stone golem's body is imbued with magical properties",
        powers=PerksStoneGolemUnique,
    ),
]

# Ice Golem
PerksIceGolemBase = PerksGolemBase.copy()
PerksIceGolemBase.remove(construct.ExplosiveCore)
PerksIceGolemBase.remove(construct.ProtectivePlating)

PerksIceGolemUnique = [
    icy.Blizzard,
    icy.FrostNova,
    icy.IcyTomb,
    icy.Frostbite,
    icy.IcyShield,
    breath.FlashFreezeBreath,
]

PerksIceGolemAttack = PerksAttackModifications.copy() + [technique.FreezingAttack]

LoadoutIceGolem = LoadoutBase + [
    PowerLoadout(
        name="Chasis",
        flavor_text="The golem's chasis has been optimized for specific use-cases",
        powers=PerksIceGolemBase,
    ),
    PowerLoadout(
        name="Offensive Modifications",
        flavor_text="The golem is equipped with various offensive capabilities",
        powers=PerksIceGolemAttack,
    ),
    PowerLoadout(
        name="Living Frost",
        flavor_text="The ice golem's body is made of enchanted, living frost",
        powers=PerksIceGolemUnique,
    ),
]

# Iron Golem
PerksIronGolemBase = PerksGolemBase.copy()
PerksIronGolemUnique = [breath.NerveGasBreath, breath.FireBreath]
PerksIronGolemAttack = PerksAttackModifications.copy() + [technique.BurningAttack]

LoadoutIronGolem = LoadoutBase + [
    PowerLoadout(
        name="Chasis",
        flavor_text="The golem's chasis has been optimized for specific use-cases",
        powers=PerksIronGolemBase,
    ),
    PowerLoadout(
        name="Offensive Modifications",
        flavor_text="The golem is equipped with various offensive capabilities",
        powers=PerksIronGolemAttack,
    ),
    PowerLoadout(
        name="Deadly Enchantments",
        flavor_text="The iron golem's body is imbued with deadly enchantments",
        powers=PerksIronGolemUnique,
    ),
]

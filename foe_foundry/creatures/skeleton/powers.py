from ...powers import PowerLoadout
from ...powers.creature import skeletal
from ...powers.creature_type import elemental, undead
from ...powers.roles import defender, leader, soldier
from ...powers.themed import (
    anti_ranged,
    cursed,
    deathly,
    fearsome,
    honorable,
    icy,
    technique,
)

PerksBasicSkeletal = skeletal.SkeletalPowers
PerksAdvancedSkeletal = skeletal.SkeletalPowers + [
    cursed.CursedWound,
    deathly.WitheringBlow,
    deathly.DrainingBlow,
    fearsome.DreadGaze,
]
PerksMartialPowers = [
    soldier.Phalanx,
    soldier.CoordinatedStrike,
    soldier.Disciplined,
    soldier.Lunge,
    soldier.PreciseStrike,
    technique.VexingAttack,
    technique.GrazingAttack,
    technique.Dueling,
    technique.PommelStrike,
    technique.BaitAndSwitch,
    technique.ParryAndRiposte,
]
PerksDefensivePowers = [
    defender.Protection,
    technique.ArmorMaster,
    technique.DisarmingAttack,
    technique.Interception,
    technique.ShieldMaster,
    anti_ranged.DeflectMissile,
    honorable.Challenge,
]
PerksFiery = [
    elemental.ElementalFireball,
    elemental.FireBurst,
    elemental.FireElementalAffinity,
    elemental.FireSmite,
    elemental.SuperheatedAura,
]
PerksChill = [
    undead.SoulChill,
    undead.StygianBurst,
    elemental.IceBurst,
    elemental.IceElementalAffinity,
    elemental.ConeOfCold,
    elemental.IceSmite,
    elemental.ArcticChillAura,
] + icy.IcyPowers
PerksLeader = [
    leader.CommandTheAttack,
    leader.CommandTheTroops,
]

LoadoutSkeleton = [
    PowerLoadout(
        name="Skeletal Boon",
        flavor_text="Rattling bones and grinning skulls",
        powers=PerksBasicSkeletal,
    ),
    PowerLoadout(
        name="Martial Memories",
        flavor_text="Half-remembered martial prowess",
        powers=PerksMartialPowers,
    ),
]

LoadoutGraveGuard = [
    PowerLoadout(
        name="Skeletal Boon",
        flavor_text="Rattling bones and grinning skulls",
        powers=PerksAdvancedSkeletal,
    ),
    PowerLoadout(
        name="Grave Guardian",
        flavor_text="Guardians of the grave, protectors of the dead",
        powers=PerksDefensivePowers,
    ),
    PowerLoadout(
        name="Martial Memories",
        flavor_text="Half-remembered martial prowess",
        powers=PerksMartialPowers,
    ),
]

LoadoutBurningSkeleton = [
    PowerLoadout(
        name="Skeletal Boon",
        flavor_text="Rattling bones and grinning skulls",
        powers=PerksBasicSkeletal,
    ),
    PowerLoadout(
        name="Burning Blade",
        flavor_text="A fiery blade",
        powers=[technique.BurningAttack],
    ),
    PowerLoadout(
        name="Black Flames",
        flavor_text="Black flames of the underworld",
        powers=PerksFiery,
    ),
]

LoadoutFreezingSkeleton = [
    PowerLoadout(
        name="Skeletal Boon",
        flavor_text="Rattling bones and grinning skulls",
        powers=PerksBasicSkeletal,
    ),
    PowerLoadout(
        name="Freezing Blade",
        flavor_text="A freezing blade",
        powers=[technique.FreezingAttack],
    ),
    PowerLoadout(
        name="Chill of the Grave",
        flavor_text="Frosty touch of the grave",
        powers=PerksChill,
    ),
]

from ...powers import PowerLoadout
from ...powers.creature import kobold
from ...powers.roles import ambusher, artillery, leader, skirmisher, soldier, support
from ...powers.spellcaster import oath
from ...powers.themed import cowardly, gadget, holy, technique, trap

PerksDraconicServants = [kobold.DraconicServants]
PerksPhalanx = [soldier.Phalanx]
PerksTraps = trap.TrapPowers
PerksDraconicStandard = [kobold.DraconicStandard]
PerksDraconicAscension = [kobold.DraconicAscension]
PerksOathAdept = [oath.OathAdept]


PerksWarrenguard = [
    soldier.PackTactics,
    technique.BaitAndSwitch,
    gadget.BasicNet,
    gadget.SmokeBomb,
    cowardly.ScurryAndScatter,
    soldier.CoordinatedStrike,
    soldier.Phalanx,
    kobold.FalseRetreat,
]
PerksSharpsnout = [
    artillery.SuppresingFire,
    artillery.Overwatch,
    ambusher.DeadlyAmbusher,
    technique.Sharpshooter,
    skirmisher.HarassingRetreat,
    technique.VexingAttack,
    technique.SlowingAttack,
    technique.DazingAttacks,
    cowardly.ScurryAndScatter,
    kobold.FalseRetreat,
]
PerksAscendant = [
    soldier.PackTactics,
    technique.GrazingAttack,
    technique.PolearmMaster,
    technique.CleavingAttack,
    gadget.FireGrenade,
    gadget.InfusedNet,
    leader.CommandTheAttack,
    technique.OverpoweringStrike,
    technique.WhirlwindOfSteel,
    soldier.CoordinatedStrike,
]
PerksWyrmcaller = [
    holy.Heroism,
    holy.WordOfRadiance,
    support.Encouragement,
    support.Guidance,
    technique.BlindingAttack,
    technique.BurningAttack,
]


LoadoutBase = [
    PowerLoadout(
        name="Draconic Servants",
        flavor_text="Unflinching servants of the True Dragon",
        powers=PerksDraconicServants,
        locked=True,
        selection_count=1,
    )
]

LoadoutWarrenguard = LoadoutBase + [
    PowerLoadout(
        name="Warrenguard",
        flavor_text="Proud defenders of the nest",
        powers=PerksWarrenguard,
    ),
    PowerLoadout(
        name="Phalanx", flavor_text="Spears united as one", powers=PerksPhalanx
    ),
]

LoadoutSharpsnout = LoadoutBase + [
    PowerLoadout(
        name="Deadly Traps",
        flavor_text="Kobolds that have mastered the art of traps",
        powers=PerksTraps,
    ),
    PowerLoadout(
        name="Sharpsnout",
        flavor_text="Kobolds that have honed their skills with the sling",
        powers=PerksSharpsnout,
    ),
]

LoadoutAscendant = LoadoutBase + [
    PowerLoadout(
        name="Ascendant",
        flavor_text="Blessed by the True Dragon",
        powers=PerksAscendant,
    ),
    PowerLoadout(
        name="Draconic Standard",
        flavor_text="A standard that inspires and empowers kobolds",
        powers=PerksDraconicStandard,
    ),
]

LoadoutWyrmcaller = LoadoutBase + [
    PowerLoadout(
        name="Oath of the Dragon",
        flavor_text="Kobolds that have sworn an oath to the True Dragon",
        powers=PerksOathAdept,
    ),
    PowerLoadout(
        name="Draconic Ascension",
        flavor_text="Witness the miracle of Draconic Ascension",
        powers=PerksDraconicAscension,
    ),
    PowerLoadout(
        name="Wyrmcaller",
        flavor_text="Preach the word of the True Dragon",
        powers=PerksWyrmcaller,
    ),
]

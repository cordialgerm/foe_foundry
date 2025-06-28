from ...powers import PowerLoadout
from ...powers.creature import wolf
from ...powers.creature_type import beast
from ...powers.roles import soldier
from ...powers.themed import bestial, breath, icy, monstrous

PerksPackTactics = [
    soldier.PackTactics,
]
PerksPackLeader = [wolf.SnappingJaws, wolf.Howl]

PerksWolfy = [
    monstrous.Pounce,
    bestial.OpportuneBite,
    bestial.RetributiveStrike,
    beast.FeedingFrenzy,
    beast.ScentOfWeakness,
    beast.WildInstinct,
]

PerksAlpha = []

PerksIcy = [icy.Blizzard, icy.IcyShield, icy.Hoarfrost]
PerksBreath = [breath.FlashFreezeBreath]


LoadoutWolf = [
    PowerLoadout(
        name="Pack Tactics",
        flavor_text="The lone wolf dies, but the pack survives.",
        powers=PerksPackTactics,
    ),
    PowerLoadout(
        name="Predator", flavor_text="Wolves are cunning hunters", powers=PerksWolfy
    ),
]

LoadoutDireWolf = LoadoutWolf + [
    PowerLoadout(
        name="Alpha",
        flavor_text="Alpha wolves lead their pack with strength and cunning.",
        powers=PerksPackLeader,
    ),
]

LoadoutFrostWolf = LoadoutDireWolf + [
    PowerLoadout(
        name="Icy Breath",
        flavor_text="Winter wolves can unleash a blast of freezing air.",
        powers=PerksBreath,
    )
]

LoadoutPacklord = LoadoutFrostWolf + [
    PowerLoadout(
        name="Fellwinte Packlord",
        flavor_text="Winter incarnate",
        powers=PerksIcy,
    )
]

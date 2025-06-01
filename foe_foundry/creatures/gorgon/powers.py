from ...powers import PowerLoadout
from ...powers.creature import gorgon
from ...powers.creature_type import beast, construct
from ...powers.roles import defender
from ...powers.themed import bestial, reckless, technique

PerksConstructed = [construct.ImmutableForm]
PerksPetrifyingBreath = [gorgon.PetrifyingBreath]

PerksHoovedAttack = [technique.ProneAttack]
PerksDeadlyCharge = [
    beast.Gore,
    bestial.Trample,
    reckless.Charger,
    reckless.Toss,
]
PerksConstructedGuardian = [
    construct.ConstructedGuardian,
    construct.ExplosiveCore,
    construct.ProtectivePlating,
    construct.SpellStoring,
    defender.SpellReflection,
    defender.ZoneOfControl,
    reckless.RelentlessEndurance,
]

LoadoutGorgon = [
    PowerLoadout(
        name="Constructed",
        flavor_text="Constructed of burnished iron",
        powers=PerksConstructed,
        locked=True,
    ),
    PowerLoadout(
        name="Petrifying Breath",
        flavor_text="Toxic, petrifying breath",
        powers=PerksPetrifyingBreath,
        locked=True,
    ),
    PowerLoadout(
        name="Hooved Attack",
        flavor_text="Iron-plated hooves",
        powers=PerksHoovedAttack,
    ),
    PowerLoadout(
        name="Deadly Charge",
        flavor_text="Fearsome hooves and deadly horns",
        powers=PerksDeadlyCharge,
    ),
    PowerLoadout(
        name="Constructed Guardian",
        flavor_text="Enchanted plating",
        powers=PerksConstructedGuardian,
    ),
]

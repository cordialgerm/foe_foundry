from foe_foundry.powers import PowerLoadout
from foe_foundry.powers.creature import zombie
from foe_foundry.powers.creature_type import giant, undead
from foe_foundry.powers.roles import bruiser
from foe_foundry.powers.themed import diseased, poison, reckless, technique

PerksUndying = [
    undead.UndeadFortitude,
    reckless.RelentlessEndurance,
    zombie.RottenFlesh,
    zombie.SeveredLimb,
]
PerksGraspingHands = [
    technique.GrapplingAttack,
    technique.ProneAttack,
    technique.PushingAttack,
]
PerksGraspingAndRottenHands = PerksGraspingHands + diseased.RottenGraspPowers

PerksStench = [
    poison.VileVomit,
    zombie.PutridStench,
    undead.StenchOfDeath,
] + diseased.ToxicBreathPowers

PerksOgre = [reckless.Toss, reckless.WildCleave, reckless.Overrun, bruiser.StunningBlow]

PerksGiant = PerksOgre + [
    giant.Boulder,
    giant.Earthshaker,
    giant.BigWindup,
    giant.GrabAndGo,
]

LoadoutZombie = [
    PowerLoadout(
        name="Undying", flavor_text="They just keep coming!", powers=PerksUndying
    ),
    PowerLoadout(
        name="Grasping Hands",
        flavor_text="Rotten hands grasping and tearing",
        powers=PerksGraspingAndRottenHands,
    ),
]

LoadoutZombieBrute = [
    PowerLoadout(
        name="Undying", flavor_text="They just keep coming!", powers=PerksUndying
    ),
    PowerLoadout(
        name="Grasping Hands",
        flavor_text="Rotten hands grasping and tearing",
        powers=PerksGraspingHands,
    ),
    PowerLoadout(
        name="Noxious Stench",
        flavor_text="Rotting and diseased flesh",
        powers=PerksStench,
    ),
]

LoadoutZombieOgre = [
    PowerLoadout(
        name="Undying", flavor_text="They just keep coming!", powers=PerksUndying
    ),
    PowerLoadout(
        name="Grasping Hands",
        flavor_text="Rotten hands grasping and tearing",
        powers=PerksGraspingAndRottenHands,
    ),
    PowerLoadout(
        name="Rotting Hulk", flavor_text="A hulking, reckless brute", powers=PerksOgre
    ),
]

LoadoutZombieGiant = [
    PowerLoadout(
        name="Undying", flavor_text="They just keep coming!", powers=PerksUndying
    ),
    PowerLoadout(
        name="Grasping Hands",
        flavor_text="Rotten hands grasping and tearing",
        powers=PerksGraspingHands,
    ),
    PowerLoadout(
        name="Rotting Hulk", flavor_text="A hulking, reckless brute", powers=PerksGiant
    ),
    PowerLoadout(
        name="Noxious Stench",
        flavor_text="Rotting and diseased flesh",
        powers=PerksStench,
    ),
]

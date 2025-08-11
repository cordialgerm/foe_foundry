from ...powers import PowerLoadout
from ...powers.creature import manticore
from ...powers.creature_type import beast
from ...powers.roles import leader
from ...powers.themed import bestial, clever, flying, monstrous

PerksSpikedTail = [manticore.SpikeVolley]

PerksCruel = [manticore.CruelJeer]

PerksAerial = [
    flying.WingedRetreat,
    flying.WingedCharge,
    flying.Flyby,
]

PerksHuntTheWeak = [
    bestial.MarkTheMeal,
    clever.IdentifyWeaknes,
    beast.FeedingFrenzy,
    monstrous.Pounce,
    monstrous.LingeringWound,
]

PerksPacklord = [
    beast.BestialRampage,
    beast.WildInstinct,
    monstrous.Frenzy,
    leader.CommandTheAttack,
]

LoadoutManticore = [
    PowerLoadout(
        name="Spiked Tail",
        flavor_text="Dozens of razor-sharp quills ready to loose",
        powers=PerksSpikedTail,
    ),
    PowerLoadout(
        name="Cruel Jeers",
        flavor_text="A mocking taunt that saps the will of its prey",
        powers=PerksCruel,
    ),
    PowerLoadout(
        name="Aerial Maneuvers",
        flavor_text="Graceful and deadly in the air",
        powers=PerksAerial,
    ),
    PowerLoadout(
        name="Hunt the Weak",
        flavor_text="A clever predator that targets the weak",
        powers=PerksHuntTheWeak,
    ),
]

LoadoutManticoreRavager = LoadoutManticore + [
    PowerLoadout(
        name="Packlord",
        flavor_text="A cunning leader that commands its pack",
        powers=PerksPacklord,
    )
]

from ...powers import PowerLoadout
from ...powers.creature import hydra
from ...powers.creature_type import beast, demon
from ...powers.themed import (
    breath,
    cruel,
    cursed,
    diseased,
    fearsome,
    monstrous,
    reckless,
    serpentine,
    technique,
)

# Hydra Heads
PerksHydraHeads = [hydra.HydraHeads]

# Aggressive
PerksAggressive = [
    beast.WildInstinct,
    beast.FeedingFrenzy,
    beast.BestialRampage,
    cruel.BloodiedFrenzy,
    fearsome.FearsomeRoar,
    monstrous.Rampage,
    monstrous.TearApart,
    reckless.Charger,
    reckless.Toss,
    serpentine.SerpentineHiss,
]

# Foul Breath
diseases = [diseased.BlindingSickness, diseased.Mindfire]
PerksDiseased = [breath.FleshMeltingBreath, technique.PoisonedAttack] + [
    d
    for d in diseased.ToxicBreathPowers
    if d.disease in diseases  # type: ignore
]

# Demonic Rage
PerksDemonicRage = [
    cursed.CursedWound,
    demon.EchoOfRage,
    demon.FeastOfSouls,
]

# Foulblooded
PerksFoulblooded = [demon.BlackBlood]

LoadoutHydra = [
    PowerLoadout(
        name="Hydra Heads",
        powers=PerksHydraHeads,
        flavor_text="A nest of deadly, writhing heads",
    ),
    PowerLoadout(
        name="Aggression", flavor_text="Always ready to attack", powers=PerksAggressive
    ),
    PowerLoadout(
        name="Foul Breath",
        flavor_text="A breath that melts flesh and poisons the mind",
        powers=PerksDiseased,
    ),
]

LoadoutHydraFoulblooded = LoadoutHydra + [
    PowerLoadout(
        name="Demonic Rage",
        flavor_text="Infected with demonic rage",
        powers=PerksDemonicRage,
    ),
    PowerLoadout(
        name="Foulblooded",
        flavor_text="Corrupted with black demon blood",
        powers=PerksFoulblooded,
    ),
]

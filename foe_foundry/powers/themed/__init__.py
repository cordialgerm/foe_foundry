from typing import List

from ..power import Power
from . import (
    aberrant,
    aquatic,
    bestial,
    breath,
    charm,
    clever,
    cruel,
    cursed,
    deathly,
    domineering,
    earthy,
    fearsome,
    flying,
    monstrous,
    organized,
    poison,
    psychic,
    reckless,
    size,
    sneaky,
    teleportation,
    tough,
    tricky,
    warrior,
)

ThemedPowers: List[Power] = (
    aberrant.AberrantPowers
    + aquatic.AquaticPowers
    + bestial.BestialPowers
    + breath.BreathPowers
    + charm.CharmPowers
    + clever.CleverPowers
    + cruel.CruelPowers
    + cursed.CursedPowers
    + deathly.DeathlyPowers
    + domineering.DomineeringPowers
    + earthy.EarthyPowers
    + fearsome.FearsomePowers
    + flying.FlyerPowers
    + monstrous.MonstrousPowers
    + organized.OrganizedPowers
    + poison.PoisonPowers
    + psychic.PsychicPowers
    + reckless.RecklessPowers
    + size.SizePowers
    + sneaky.SneakyPowers
    + tricky.TrickyPowers
    + teleportation.TeleportationPowers
    + tough.ToughPowers
    + warrior.WarriorPowers
)

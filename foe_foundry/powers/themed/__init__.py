from typing import List

from ..power import Power
from . import (
    aberrant,
    bestial,
    breath,
    charm,
    cursed,
    deathly,
    domineering,
    fearsome,
    monstrous,
    organized,
    poison,
    psychic,
    sneaky,
    teleportation,
    tough,
    tricky,
    warrior,
)

ThemedPowers: List[Power] = (
    aberrant.AberrantPowers
    + bestial.BestialPowers
    + breath.BreathPowers
    + charm.CharmPowers
    + cursed.CursedPowers
    + deathly.DeathlyPowers
    + domineering.DomineeringPowers
    + fearsome.FearsomePowers
    + monstrous.MonstrousPowers
    + organized.OrganizedPowers
    + poison.PoisonPowers
    + psychic.PsychicPowers
    + sneaky.SneakyPowers
    + tricky.TrickyPowers
    + teleportation.TeleportationPowers
    + tough.ToughPowers
    + warrior.WarriorPowers
)

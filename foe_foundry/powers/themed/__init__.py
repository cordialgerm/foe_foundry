from typing import List

from ..power import Power
from . import (
    aberrant,
    bestial,
    breath,
    charm,
    cursed,
    deathly,
    fearsome,
    monstrous,
    organized,
    poison,
    psychic,
    teleportation,
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
    + fearsome.FearsomePowers
    + monstrous.MonstrousPowers
    + organized.OrganizedPowers
    + poison.PoisonPowers
    + psychic.PsychicPowers
    + tricky.TrickyPowers
    + teleportation.TeleportationPowers
    + warrior.WarriorPowers
)

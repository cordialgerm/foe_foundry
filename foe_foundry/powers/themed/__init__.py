from typing import List

from ..power import Power
from . import (
    aberrant,
    aquatic,
    bestial,
    breath,
    chaotic,
    charm,
    clever,
    cruel,
    cursed,
    deathly,
    domineering,
    earthy,
    fearsome,
    flying,
    gadget,
    monstrous,
    organized,
    poison,
    psychic,
    reckless,
    size,
    sneaky,
    storm,
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
    + chaotic.ChaoticPowers
    + charm.CharmPowers
    + clever.CleverPowers
    + cruel.CruelPowers
    + cursed.CursedPowers
    + deathly.DeathlyPowers
    + domineering.DomineeringPowers
    + earthy.EarthyPowers
    + fearsome.FearsomePowers
    + flying.FlyerPowers
    + gadget.GadgetPowers
    + monstrous.MonstrousPowers
    + organized.OrganizedPowers
    + poison.PoisonPowers
    + psychic.PsychicPowers
    + reckless.RecklessPowers
    + size.SizePowers
    + sneaky.SneakyPowers
    + storm.StormPowers
    + tricky.TrickyPowers
    + teleportation.TeleportationPowers
    + tough.ToughPowers
    + warrior.WarriorPowers
)

from typing import List

from ..power import Power
from . import (
    aberrant,
    aquatic,
    attack,
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
    temporal,
    tough,
    trap,
    tricky,
    warrior,
)

ThemedPowers: List[Power] = (
    aberrant.AberrantPowers
    + aquatic.AquaticPowers
    + attack.AttackPowers
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
    + teleportation.TeleportationPowers
    + temporal.TemporalPowers
    + tough.ToughPowers
    + trap.TrapPowers
    + tricky.TrickyPowers
    + warrior.WarriorPowers
)

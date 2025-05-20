from typing import List

from ..power import Power
from . import (
    aberrant,
    anti_magic,
    anti_ranged,
    aquatic,
    bestial,
    breath,
    chaotic,
    charm,
    clever,
    cowardly,
    cruel,
    cursed,
    deathly,
    diseased,
    domineering,
    earthy,
    emanation,
    fast,
    fearsome,
    flying,
    gadget,
    holy,
    honorable,
    icy,
    illusory,
    monstrous,
    petrifying,
    poison,
    psychic,
    reckless,
    serpentine,
    sneaky,
    storm,
    technique,
    teleportation,
    temporal,
    thuggish,
    totemic,
    tough,
    trap,
)

ThemedPowers: List[Power] = (
    aberrant.AberrantPowers
    + anti_magic.AntiMagicPowers
    + anti_ranged.AntiRangedPowers
    + aquatic.AquaticPowers
    + bestial.BestialPowers
    + breath.BreathPowers
    + chaotic.ChaoticPowers
    + charm.CharmPowers
    + clever.CleverPowers
    + cruel.CruelPowers
    + cursed.CursedPowers
    + cowardly.CowardlyPowers
    + deathly.DeathlyPowers
    + diseased.DiseasedPowers
    + domineering.DomineeringPowers
    + earthy.EarthyPowers
    + emanation.EmanationPowers
    + fast.FastPowers
    + fearsome.FearsomePowers
    + flying.FlyingPowers
    + gadget.GadgetPowers
    + holy.HolyPowers
    + honorable.HonorablePowers
    + icy.IcyPowers
    + monstrous.MonstrousPowers
    + petrifying.PetrifyingPowers
    + poison.PoisonPowers
    + psychic.PsychicPowers
    + reckless.RecklessPowers
    + serpentine.SerpentinePowers
    + sneaky.SneakyPowers
    + storm.StormPowers
    + technique.TechniquePowers
    + teleportation.TeleportationPowers
    + temporal.TemporalPowers
    + totemic.TotemicPowers
    + thuggish.ThuggishPowers
    + tough.ToughPowers
    + trap.TrapPowers
    + illusory.IllusoryPowers
)

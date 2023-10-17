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
    classes,
    clever,
    cruel,
    cursed,
    deathly,
    domineering,
    earthy,
    fast,
    fearsome,
    fighting_styles,
    flying,
    gadget,
    holy,
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
    + classes.ClassPowers
    + clever.CleverPowers
    + cruel.CruelPowers
    + cursed.CursedPowers
    + deathly.DeathlyPowers
    + domineering.DomineeringPowers
    + earthy.EarthyPowers
    + fast.FastPowers
    + fearsome.FearsomePowers
    + fighting_styles.FightingStylePowers
    + flying.FlyerPowers
    + gadget.GadgetPowers
    + holy.HolyPowers
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

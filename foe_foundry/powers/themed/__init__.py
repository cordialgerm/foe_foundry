from typing import List

from ..power import Power
from . import (
    aberrant,
    anti_magic,
    aquatic,
    attack,
    bestial,
    chaotic,
    charm,
    classes,
    clever,
    cruel,
    cursed,
    deathly,
    diseased,
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
    + anti_magic.AntiMagicPowers
    + aquatic.AquaticPowers
    + attack.AttackPowers
    + bestial.BestialPowers
    + chaotic.ChaoticPowers
    + charm.CharmPowers
    + classes.ClassPowers
    + clever.CleverPowers
    + cruel.CruelPowers
    + cursed.CursedPowers
    + deathly.DeathlyPowers
    + diseased.DiseasedPowers
    + domineering.DomineeringPowers
    + earthy.EarthyPowers
    + fast.FastPowers
    + fearsome.FearsomePowers
    + fighting_styles.FightingStylePowers
    + flying.FlyingPowers
    + gadget.GadgetPowers
    + holy.HolyPowers
    + monstrous.MonstrousPowers
    + organized.OrganizedPowers
    + poison.PoisonPowers
    + psychic.PsychicPowers
    + reckless.RecklessPowers
    + sneaky.SneakyPowers
    + storm.StormPowers
    + teleportation.TeleportationPowers
    + temporal.TemporalPowers
    + tough.ToughPowers
    + trap.TrapPowers
    + tricky.TrickyPowers
    + warrior.WarriorPowers
)

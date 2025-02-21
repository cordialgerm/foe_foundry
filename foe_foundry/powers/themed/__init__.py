from typing import List

from ..power import Power
from . import (
    aberrant,
    anti_magic,
    anti_ranged,
    aquatic,
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
    flying,
    gadget,
    holy,
    magic,
    monstrous,
    organized,
    poison,
    psychic,
    reckless,
    skeletal,
    sneaky,
    species,
    spellcaster,
    storm,
    technique,
    teleportation,
    temporal,
    tough,
    trap,
    tricky,
    warrior,
    zombie,
)

ThemedPowers: List[Power] = (
    aberrant.AberrantPowers
    + anti_magic.AntiMagicPowers
    + anti_ranged.AntiRangedPowers
    + aquatic.AquaticPowers
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
    + flying.FlyingPowers
    + gadget.GadgetPowers
    + holy.HolyPowers
    + magic.MagicPowers
    + monstrous.MonstrousPowers
    + organized.OrganizedPowers
    + poison.PoisonPowers
    + psychic.PsychicPowers
    + reckless.RecklessPowers
    + skeletal.SkeletalPowers
    + sneaky.SneakyPowers
    + species.DwarfPowers
    + species.OrcPowers
    + spellcaster.SpellcasterPowers
    + storm.StormPowers
    + technique.TechniquePowers
    + teleportation.TeleportationPowers
    + temporal.TemporalPowers
    + tough.ToughPowers
    + trap.TrapPowers
    + tricky.TrickyPowers
    + warrior.WarriorPowers
    + zombie.ZombiePowers
)

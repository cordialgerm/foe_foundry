from foe_foundry.powers.creatures import CreaturePowers
from foe_foundry.powers.roles import RolePowers
from foe_foundry.powers.themed import (
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
)

# TODO - add all powers
AllPowers = (
    CreaturePowers
    + RolePowers
    + aberrant.AberrantPowers
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
)

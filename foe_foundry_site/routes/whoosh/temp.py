from foe_foundry.powers.creatures import CreaturePowers
from foe_foundry.powers.roles import RolePowers
from foe_foundry.powers.themed import aberrant, anti_magic, aquatic, attack, bestial, chaotic

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
)

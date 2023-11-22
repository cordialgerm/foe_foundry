from foe_foundry.powers.creatures import CreaturePowers
from foe_foundry.powers.roles import ambusher, artillery

# TODO - add all powers
AllPowers = (
    # creature powers
    CreaturePowers
    # role powers
    + ambusher.AmbusherPowers
    + artillery.ArtilleryPowers
)

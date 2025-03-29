from .balor import BalorPowers
from .basilisk import BasiliskPowers
from .goblin import GoblinPowers
from .gorgon import GorgonPowers
from .guard import GuardPowers
from .hydra import HydraPowers
from .mage import MagePowers
from .skeletal import SkeletalPowers
from .spider import SpiderPowers
from .vrock import VrockPowers
from .warrior import WarriorPowers
from .wolf import WolfPowers
from .zombie import ZombiePowers

CreaturePowers = (
    SkeletalPowers
    + WarriorPowers
    + ZombiePowers
    + GuardPowers
    + MagePowers
    + HydraPowers
    + BasiliskPowers
    + GorgonPowers
    + VrockPowers
    + GoblinPowers
    + BalorPowers
    + SpiderPowers
    + WolfPowers
)

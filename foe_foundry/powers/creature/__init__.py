from .skeletal import SkeletalPowers  # noqa
from .warrior import WarriorPowers  # noqa
from .zombie import ZombiePowers  # noqa
from .guard import GuardPowers  # noqa
from .mage import MagePowers  # noqa
from .hydra import HydraPowers  # noqa
from .basilisk import BasiliskPowers  # noqa

CreaturePowers = (
    SkeletalPowers
    + WarriorPowers
    + ZombiePowers
    + GuardPowers
    + MagePowers
    + HydraPowers
    + BasiliskPowers
)

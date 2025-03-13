from .skeletal import SkeletalPowers  # noqa
from .warrior import WarriorPowers  # noqa
from .zombie import ZombiePowers  # noqa
from .guard import GuardPowers  # noqa
from .mage import MagePowers  # noqa

CreaturePowers = (
    SkeletalPowers + WarriorPowers + ZombiePowers + GuardPowers + MagePowers
)

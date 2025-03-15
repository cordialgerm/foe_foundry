from .assassin import AssassinTemplate
from .balor import BalorTemplate
from .bandit import BanditTemplate
from .basilisk import BasiliskTemplate
from .berserker import BerserkerTemplate
from .cultist import CultistTemplate
from .golem import GolemTemplate
from .guard import GuardTemplate
from .hydra import HydraTemplate
from .mage import MageTemplate
from .priest import PriestTemplate
from .scout import ScoutTemplate
from .skeleton import SkeletonTemplate
from .spy import SpyTemplate
from .template import CreatureTemplate
from .tough import ToughTemplate
from .warrior import WarriorTemplate
from .zombie import ZombieTemplate

AllTemplates: list[CreatureTemplate] = [
    AssassinTemplate,
    BalorTemplate,
    BanditTemplate,
    BasiliskTemplate,
    BerserkerTemplate,
    CultistTemplate,
    GolemTemplate,
    GuardTemplate,
    HydraTemplate,
    MageTemplate,
    PriestTemplate,
    ScoutTemplate,
    SkeletonTemplate,
    SpyTemplate,
    ToughTemplate,
    WarriorTemplate,
    ZombieTemplate,
]

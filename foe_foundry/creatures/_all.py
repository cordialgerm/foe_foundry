from .assassin import AssassinTemplate
from .bandit import BanditTemplate
from .berserker import BerserkerTemplate
from .cultist import CultistTemplate
from .golem import GolemTemplate
from .guard import GuardTemplate
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
    BanditTemplate,
    BerserkerTemplate,
    CultistTemplate,
    GolemTemplate,
    GuardTemplate,
    PriestTemplate,
    ScoutTemplate,
    SkeletonTemplate,
    SpyTemplate,
    ToughTemplate,
    WarriorTemplate,
    ZombieTemplate,
]

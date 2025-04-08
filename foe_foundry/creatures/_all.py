from .animated_armor import AnimatedArmorTemplate
from .assassin import AssassinTemplate
from .balor import BalorTemplate
from .bandit import BanditTemplate
from .basilisk import BasiliskTemplate
from .berserker import BerserkerTemplate
from .bugbear import BugbearTemplate
from .cultist import CultistTemplate
from .dire_bunny import DireBunnyTemplate
from .druid import DruidTemplate
from .ghoul import GhoulTemplate
from .goblin import GoblinTemplate
from .golem import GolemTemplate
from .gorgon import GorgonTemplate
from .guard import GuardTemplate
from .hydra import HydraTemplate
from .knight import KnightTemplate
from .mage import MageTemplate
from .medusa import MedusaTemplate
from .nothic import HollowGazerTemplate
from .ogre import OgreTemplate
from .orc import OrcTemplate
from .priest import PriestTemplate
from .scout import ScoutTemplate
from .simulacrum import SimulacrumTemplate
from .skeleton import SkeletonTemplate
from .spy import SpyTemplate
from .template import CreatureTemplate, GenerationSettings
from .tough import ToughTemplate
from .vrock import VrockTemplate
from .warrior import WarriorTemplate
from .wolf import WolfTemplate
from .zombie import ZombieTemplate

AllTemplates: list[CreatureTemplate] = [
    AnimatedArmorTemplate,
    AssassinTemplate,
    BalorTemplate,
    BanditTemplate,
    BasiliskTemplate,
    BerserkerTemplate,
    BugbearTemplate,
    CultistTemplate,
    DireBunnyTemplate,
    DruidTemplate,
    GolemTemplate,
    GorgonTemplate,
    GuardTemplate,
    GhoulTemplate,
    GoblinTemplate,
    HollowGazerTemplate,
    HydraTemplate,
    KnightTemplate,
    MageTemplate,
    MedusaTemplate,
    OgreTemplate,
    OrcTemplate,
    PriestTemplate,
    ScoutTemplate,
    SimulacrumTemplate,
    SkeletonTemplate,
    SpyTemplate,
    ToughTemplate,
    VrockTemplate,
    WarriorTemplate,
    WolfTemplate,
    ZombieTemplate,
]


def all_templates_and_settings() -> list[
    tuple[CreatureTemplate, list[GenerationSettings]]
]:
    results = []
    for template in AllTemplates:
        for setting in template.generate_settings():
            results.append((template, setting))
    return results

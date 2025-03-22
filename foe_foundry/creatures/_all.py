from .assassin import AssassinTemplate
from .balor import BalorTemplate
from .bandit import BanditTemplate
from .basilisk import BasiliskTemplate
from .berserker import BerserkerTemplate
from .cultist import CultistTemplate
from .golem import GolemTemplate
from .gorgon import GorgonTemplate
from .guard import GuardTemplate
from .hydra import HydraTemplate
from .knight import KnightTemplate
from .mage import MageTemplate
from .medusa import MedusaTemplate
from .priest import PriestTemplate
from .scout import ScoutTemplate
from .skeleton import SkeletonTemplate
from .spy import SpyTemplate
from .template import CreatureTemplate, GenerationSettings
from .tough import ToughTemplate
from .vrock import VrockTemplate
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
    GorgonTemplate,
    GuardTemplate,
    HydraTemplate,
    KnightTemplate,
    MageTemplate,
    MedusaTemplate,
    PriestTemplate,
    ScoutTemplate,
    SkeletonTemplate,
    SpyTemplate,
    ToughTemplate,
    VrockTemplate,
    WarriorTemplate,
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

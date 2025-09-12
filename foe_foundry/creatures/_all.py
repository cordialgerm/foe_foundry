from ._data import GenerationSettings
from ._template import MonsterTemplate
from .animated_armor import AnimatedArmorTemplate
from .assassin import AssassinTemplate
from .balor import BalorTemplate
from .bandit import BanditTemplate
from .basilisk import BasiliskTemplate
from .berserker import BerserkerTemplate
from .bugbear import BugbearTemplate
from .chimera import ChimeraTemplate
from .cultist import CultistTemplate
from .dire_bunny import DireBunnyTemplate
from .druid import DruidTemplate
from .frost_giant import FrostGiantTemplate
from .gelatinous_cube import GelatinousCubeTemplate
from .ghoul import GhoulTemplate
from .goblin import GoblinTemplate
from .golem import GolemTemplate
from .gorgon import GorgonTemplate
from .guard import GuardTemplate
from .hollow_gazer import HollowGazerTemplate
from .hydra import HydraTemplate
from .knight import KnightTemplate
from .kobold import KoboldTemplate
from .lich import LichTemplate
from .mage import MageTemplate
from .manticore import ManticoreTemplate
from .medusa import MedusaTemplate
from .merrow import MerrowTemplate
from .mimic import MimicTemplate
from .ogre import OgreTemplate
from .orc import OrcTemplate
from .owlbear import OwlbearTemplate
from .priest import PriestTemplate
from .scout import ScoutTemplate
from .simulacrum import SimulacrumTemplate
from .skeleton import SkeletonTemplate
from .spirit import SpiritTemplate
from .spy.spy import SpyTemplate
from .thug import ThugTemplate
from .vrock.vrock import VrockTemplate
from .warrior import WarriorTemplate
from .wight import WightTemplate
from .wolf import WolfTemplate
from .zombie import ZombieTemplate

AllTemplates: list[MonsterTemplate] = [
    AnimatedArmorTemplate,
    AssassinTemplate,
    BalorTemplate,
    BanditTemplate,
    BasiliskTemplate,
    BerserkerTemplate,
    BugbearTemplate,
    ChimeraTemplate,
    CultistTemplate,
    DireBunnyTemplate,
    DruidTemplate,
    FrostGiantTemplate,
    GelatinousCubeTemplate,
    GolemTemplate,
    GorgonTemplate,
    GuardTemplate,
    GhoulTemplate,
    GoblinTemplate,
    HollowGazerTemplate,
    HydraTemplate,
    KnightTemplate,
    KoboldTemplate,
    LichTemplate,
    MageTemplate,
    ManticoreTemplate,
    MedusaTemplate,
    MerrowTemplate,
    MimicTemplate,
    OgreTemplate,
    OrcTemplate,
    OwlbearTemplate,
    PriestTemplate,
    ScoutTemplate,
    SimulacrumTemplate,
    SkeletonTemplate,
    SpiritTemplate,
    SpyTemplate,
    ThugTemplate,
    VrockTemplate,
    WarriorTemplate,
    WightTemplate,
    WolfTemplate,
    ZombieTemplate,
]

TemplatesByKey: dict[str, MonsterTemplate] = {
    template.key: template for template in AllTemplates
}


def all_templates_and_settings() -> (
    list[tuple[MonsterTemplate, list[GenerationSettings]]]
):
    results = []
    for template in AllTemplates:
        for setting in template.generate_settings():
            results.append((template, setting))
    return results

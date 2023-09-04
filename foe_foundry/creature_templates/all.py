from typing import List

from .aberration import AberrationTemplate
from .beast import BeastTemplate
from .celestial import CelestialTemplate
from .construct import ConstructTemplate
from .dragon import DragonTemplate
from .elemental import ElementalTemplate
from .fey import FeyTemplate
from .fiend import FiendTemplate
from .giant import GiantTemplate
from .humanoid import HumanoidTemplate
from .monstrosity import MonstrosityTemplate
from .ooze import OozeTemplate
from .template import CreatureTypeTemplate

AllCreatureTemplates: List[CreatureTypeTemplate] = [
    AberrationTemplate,
    BeastTemplate,
    CelestialTemplate,
    ConstructTemplate,
    DragonTemplate,
    ElementalTemplate,
    FeyTemplate,
    FiendTemplate,
    GiantTemplate,
    HumanoidTemplate,
    MonstrosityTemplate,
    OozeTemplate,
]

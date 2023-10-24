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
from .plant import PlantTemplate
from .template import CreatureTypeTemplate
from .undead import UndeadTemplate

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
    PlantTemplate,
    UndeadTemplate,
]

__lookup = {a.name.lower(): a for a in AllCreatureTemplates}


def get_creature_template(name: str) -> CreatureTypeTemplate:
    t = __lookup.get(name, None)
    if t is None:
        raise ValueError(f"No creature template found for '{name}'")
    return t

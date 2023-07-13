from typing import List

from .aberration import AberrationTemplate
from .beast import BeastTemplate
from .celestial import CelestialTemplate
from .construct import ConstructTemplate
from .template import CreatureTypeTemplate

AllCreatureTemplates: List[CreatureTypeTemplate] = [
    AberrationTemplate,
    BeastTemplate,
    CelestialTemplate,
    ConstructTemplate,
]

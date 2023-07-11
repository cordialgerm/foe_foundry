from typing import List

from .aberration import AberrationTemplate
from .beast import BeastTemplate
from .template import CreatureTypeTemplate

AllCreatureTemplates: List[CreatureTypeTemplate] = [AberrationTemplate, BeastTemplate]

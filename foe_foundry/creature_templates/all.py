from typing import List

from .aberration import AberrationTemplate
from .template import CreatureTypeTemplate


def all_creature_templates() -> List[CreatureTypeTemplate]:
    return [AberrationTemplate()]

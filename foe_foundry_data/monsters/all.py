import os
from functools import cached_property

from foe_foundry.creatures import AllTemplates

from .data import CreatureTemplateModel


class MonsterLookupCache:
    """Caches power lookups for faster access because it can require creating a new statblock, which is expensive"""

    def __init__(self):
        base_url = os.environ.get("SITE_URL")
        if base_url is None:
            raise ValueError("SITE_URL environment variable is not set")
        self.base_url = base_url

    @cached_property
    def CreatureTemplateLookup(self) -> dict[str, CreatureTemplateModel]:
        return {
            template.key: CreatureTemplateModel.from_template(template, self.base_url)
            for template in AllTemplates
        }

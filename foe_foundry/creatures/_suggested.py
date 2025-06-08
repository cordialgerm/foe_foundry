import numpy as np

from ..creature_types import CreatureType
from ..creatures import SelectionSettings
from ..statblocks import Statblock
from .balor.balor import BalorTemplate
from .chimera.chimera import ChimeraTemplate
from .druid import DruidTemplate
from .gelatinous_cube import GelatinousCubeTemplate
from .golem import GolemTemplate
from .knight import KnightTemplate
from .kobold import KoboldTemplate
from .nothic import HollowGazerTemplate
from .ogre import OgreTemplate
from .warrior import WarriorTemplate
from .wight import WightTemplate
from .wolf import WolfTemplate


class _DefaultStatblockCache:
    def __init__(self):
        self.cache = {}

    def get(self, creature_type: CreatureType, requested_cr: float) -> Statblock:
        if (creature_type, requested_cr) not in self.cache:
            self.cache[(creature_type, requested_cr)] = (
                self._do_default_statblock_for_creature_type(
                    creature_type, requested_cr
                )
            )
        return self.cache[(creature_type, requested_cr)]

    def _do_default_statblock_for_creature_type(
        self, creature_type: CreatureType, requested_cr: float
    ) -> Statblock:
        """
        Returns the default template and settings for a given creature type.
        """
        if creature_type == CreatureType.Aberration:
            template = HollowGazerTemplate
        elif creature_type == CreatureType.Beast:
            template = WolfTemplate
        elif creature_type == CreatureType.Celestial:
            template = KnightTemplate
        elif creature_type == CreatureType.Construct:
            template = GolemTemplate
        elif creature_type == CreatureType.Dragon:
            template = KoboldTemplate  # TODO
        elif creature_type == CreatureType.Elemental:
            template = DruidTemplate  # TODO
        elif creature_type == CreatureType.Fey:
            template = DruidTemplate  # TODO
        elif creature_type == CreatureType.Fiend:
            template = BalorTemplate
        elif creature_type == CreatureType.Giant:
            template = OgreTemplate
        elif creature_type == CreatureType.Humanoid:
            template = WarriorTemplate
        elif creature_type == CreatureType.Monstrosity:
            template = ChimeraTemplate
        elif creature_type == CreatureType.Ooze:
            template = GelatinousCubeTemplate
        elif creature_type == CreatureType.Plant:
            template = DruidTemplate  # TODO
        elif creature_type == CreatureType.Undead:
            template = WightTemplate
        else:
            raise ValueError(f"Unknown creature type: {creature_type}")

        crs = []
        settings = []
        for setting in template.generate_settings(
            selection_settings=SelectionSettings(retries=1)
        ):
            settings.append(setting)
            crs.append(setting.cr)

        crs = np.array(crs)
        err = np.pow(crs - requested_cr, 2)
        min_index = np.argmin(err)

        return template.generate(settings[min_index]).finalize()


_cache = _DefaultStatblockCache()


def default_statblock_for_creature_type(
    creature_type: CreatureType, requested_cr: float
) -> Statblock:
    """
    Returns the default template and settings for a given creature type.
    """
    return _cache.get(creature_type, requested_cr)

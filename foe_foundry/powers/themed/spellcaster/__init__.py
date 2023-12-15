from typing import List

from ...power import Power
from . import abjurer, celestial, divination, enchanter, fiendish, necromancer

SpellcasterPowers: List[Power] = (
    celestial.CelestialCasters()
    + divination.DivinationWizards()
    + fiendish.FiendishCasters()
    + enchanter.EnchanterWizards()
    + necromancer.NecromancerWizards()
    + abjurer.AbjurationWizards()
)

from typing import List

from ...power import Power
from . import (
    abjurer,
    celestial,
    conjurer,
    divination,
    elementalist,
    enchanter,
    fiendish,
    illusionist,
    necromancer,
    psionic,
    transmuter,
)

SpellcasterPowers: List[Power] = (
    abjurer.AbjurationWizards()
    + celestial.CelestialCasters()
    + conjurer.ConjurationWizards()
    + divination.DivinationWizards()
    + elementalist.ElementalistWizards()
    + enchanter.EnchanterWizards()
    + fiendish.FiendishCasters()
    + illusionist.IllusionistWizards()
    + necromancer.NecromancerWizards()
    + psionic.PsionicCasters()
    + transmuter.TransmutationWizards()
)

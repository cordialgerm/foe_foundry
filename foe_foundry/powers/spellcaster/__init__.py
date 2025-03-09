from typing import List

from ..power import Power
from . import (
    abjurer,
    celestial,
    conjurer,
    cult,
    divination,
    elementalist,
    enchanter,
    fiendish,
    illusionist,
    magic,
    metamagic,
    necromancer,
    psionic,
    transmuter,
)
from .base import WizardPower  # noqa

SpellcasterPowers: List[Power] = (
    abjurer.AbjurationWizards()
    + celestial.CelestialCasters()
    + conjurer.ConjurationWizards()
    + cult.CultCasters()
    + divination.DivinationWizards()
    + elementalist.ElementalistWizards
    + enchanter.EnchanterWizards()
    + fiendish.FiendishCasters()
    + illusionist.IllusionistWizards()
    + magic.MagicPowers
    + metamagic.MetamagicPowers
    + necromancer.NecromancerWizards()
    + psionic.PsionicCasters()
    + transmuter.TransmutationWizards()
)

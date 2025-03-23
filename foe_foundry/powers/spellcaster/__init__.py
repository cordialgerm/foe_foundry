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
    oath,
    psionic,
    shaman,
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
    + oath.OathCasters()
    + necromancer.NecromancerWizards()
    + psionic.PsionicCasters()
    + shaman.ShamanPowers
    + transmuter.TransmutationWizards()
)

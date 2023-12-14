from typing import List

from ...power import Power
from . import divination

WizardPowers: List[Power] = [] + divination.DivinationWizards()

from .dwarf import DwarfPowers  # noqa
from .orc import OrcPowers  # noqa
from ..power import Power

SpeciesPowers: list[Power] = DwarfPowers + OrcPowers

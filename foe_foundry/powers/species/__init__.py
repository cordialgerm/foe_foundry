from .dwarf import DwarfPowers  # noqa
from .orc import OrcPowers  # noqa
from .halfling import HalflingPowers  # noqa
from ..power import Power
from .gnome import GnomePowers

SpeciesPowers: list[Power] = DwarfPowers + OrcPowers + HalflingPowers + GnomePowers

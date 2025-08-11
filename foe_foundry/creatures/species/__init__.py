from .dwarf import DwarfSpecies
from .gnome import GnomeSpecies
from .halfling import HalflingSpecies
from .human import HumanSpecies
from .orc import OrcSpecies
from .species import CreatureSpecies

AllSpecies: list[CreatureSpecies] = [
    HumanSpecies,
    DwarfSpecies,
    OrcSpecies,
    GnomeSpecies,
    HalflingSpecies,
]

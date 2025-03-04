from .creature import CreaturePowers
from .creature_type import CreatureTypePowers
from .roles import RolePowers
from .species import SpeciesPowers
from .spellcaster import SpellcasterPowers
from .themed import ThemedPowers

AllPowers = (
    ThemedPowers
    + RolePowers
    + CreatureTypePowers
    + SpeciesPowers
    + CreaturePowers
    + SpellcasterPowers
)

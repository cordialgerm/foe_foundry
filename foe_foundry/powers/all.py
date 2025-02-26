from .creature_type import CreatureTypePowers
from .roles import RolePowers
from .species import SpeciesPowers
from .themed import ThemedPowers
from .creature import CreaturePowers

AllPowers = ThemedPowers + RolePowers + CreatureTypePowers + SpeciesPowers + CreaturePowers

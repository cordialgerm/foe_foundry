from typing import List

from .ambusher import Ambusher
from .artillery import Artillery
from .bruiser import Bruiser
from .controller import Controller
from .defender import Defender
from .leader import Leader
from .skirmisher import Skirmisher
from .template import RoleTemplate, RoleVariant

# TODO - add roles here as powers are implemented
AllRoles: List[RoleTemplate] = [
    Ambusher,
    Artillery,
    Bruiser,
    Controller,
    Defender,
    # Leader,
    # Skirmisher,
]

AllRoleVariants: List[RoleVariant] = [rv for r in AllRoles for rv in r.variants]

_Lookup = {r.key: r for r in AllRoles}


def get_role(key: str) -> RoleTemplate:
    return _Lookup[key]

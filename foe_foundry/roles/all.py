from typing import List

from .ambusher import Ambusher
from .artillery import Artillery
from .bruiser import Bruiser
from .controller import Controller
from .defender import Defender
from .leader import Leader
from .skirmisher import Skirmisher
from .template import RoleTemplate

AllRoles: List[RoleTemplate] = [
    Ambusher,
    Artillery,
    Bruiser,
    Controller,
    Defender,
    Leader,
    Skirmisher,
]

_Lookup = {r.key: r for r in AllRoles}


def get_role(key: str) -> RoleTemplate:
    role = _Lookup.get(key.lower())
    if role is None:
        raise ValueError(f"Unsupported role '{key}'")
    return role

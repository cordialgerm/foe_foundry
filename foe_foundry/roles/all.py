from typing import List

from .ambusher import Ambusher
from .artillery import Artillery
from .bruiser import Bruiser
from .controller import Controller
from .defender import Defender
from .leader import Leader
from .skirmisher import Skirmisher
from .template import RoleTemplate, RoleVariant


def all_roles() -> List[RoleTemplate]:
    return [Ambusher, Artillery, Bruiser, Controller, Defender, Leader, Skirmisher]


def all_role_variants() -> List[RoleVariant]:
    variants = []
    for role in all_roles():
        for variant in role.variants:
            variants.append(variant)
    return variants

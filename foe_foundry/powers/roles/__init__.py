from typing import List

from ..power import Power
from .ambusher import AmbusherPowers
from .artillery import ArtilleryPowers
from .bruiser import BruiserPowers
from .controller import ControllerPowers
from .defender import DefenderPowers
from .leader import LeaderPowers
from .skirmisher import SkirmisherPowers
from .soldier import SoldierPowers
from .support import SupportPowers

RolePowers: List[Power] = (
    AmbusherPowers
    + ArtilleryPowers
    + BruiserPowers
    + ControllerPowers
    + DefenderPowers
    + LeaderPowers
    + SkirmisherPowers
    + SupportPowers
    + SoldierPowers
)

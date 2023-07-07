import pytest

from foundry_of_foes import (
    BaseStatblock,
    MonsterDials,
    as_ambusher_cycle,
    as_artillery_cycle,
    as_bruiser_cycle,
    as_controller_cycle,
    as_defender_cycle,
    as_leader_cycle,
    as_skirmisher_cycle,
    general_use_stats,
)


@pytest.mark.parametrize("name,stats", general_use_stats.AllNamed)
def test_minion(name: str, stats: BaseStatblock):
    ambusher1 = as_ambusher_cycle(stats)
    ambusher2 = as_ambusher_cycle(stats)

    artillery1 = as_artillery_cycle(stats)
    artillery2 = as_artillery_cycle(stats)
    artillery3 = as_artillery_cycle(stats)
    artillery4 = as_artillery_cycle(stats)

    bruiser1 = as_bruiser_cycle(stats)
    bruiser2 = as_bruiser_cycle(stats)
    bruiser3 = as_bruiser_cycle(stats)

    controller1 = as_controller_cycle(stats)

    defender1 = as_defender_cycle(stats)
    defender2 = as_defender_cycle(stats)
    defender3 = as_defender_cycle(stats)
    defender4 = as_defender_cycle(stats)

    ## leader
    leader1 = as_leader_cycle(stats)
    leader2 = as_leader_cycle(stats)
    leader3 = as_leader_cycle(stats)

    ## skirmisher
    skirmisher1 = as_skirmisher_cycle(stats)
    skirmisher2 = as_skirmisher_cycle(stats)

from foe_foundry.attributes import Stats, StatScaling
from foe_foundry.creatures import base_stats
from foe_foundry.statblocks.common import All


def test_all_stats():
    for common in All:
        base_stat = base_stats(
            name=f"sample_{common.cr}",
            cr=common.cr,
            stats=[
                Stats.STR.scaler(StatScaling.Primary),
                Stats.DEX.scaler(StatScaling.Medium),
                Stats.INT.scaler(StatScaling.Default),
                Stats.WIS.scaler(StatScaling.Medium),
                Stats.CHA.scaler(StatScaling.Low, -2),
            ],
        )
        assert base_stat is not None

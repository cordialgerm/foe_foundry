from foe_foundry import DamageType


def test_all_types():
    assert len(DamageType.All()) == 13

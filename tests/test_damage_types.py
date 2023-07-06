from foundry_of_foes.damage import DamageType


def test_all_types():
    assert len(DamageType.All()) == 13

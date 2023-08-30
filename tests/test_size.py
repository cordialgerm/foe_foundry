from foe_foundry import Size


def test_size_comparison():
    assert Size.Tiny <= Size.Small
    assert Size.Tiny < Size.Small
    assert Size.Small > Size.Tiny
    assert Size.Small >= Size.Tiny
    assert Size.Small != Size.Tiny
    assert Size.Small == Size.Small

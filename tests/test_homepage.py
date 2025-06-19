from foe_foundry_data.homepage import load_homepage_data


def test_load_homepage_data():
    data = load_homepage_data()

    assert len(data.monsters) > 10
    assert len(data.powers) > 500
    assert len(data.blogs) >= 10

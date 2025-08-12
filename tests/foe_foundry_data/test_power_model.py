from foe_foundry_data.powers import Powers


def test_all_powers_have_icons():
    for k, p in Powers.PowerLookup.items():
        assert p.icon_path is not None, f"Power {k} does not have an icon"

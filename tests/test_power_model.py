from foe_foundry_data.powers import Powers, clean_power_index, search_powers


def test_search_for_powers():
    try:
        clean_power_index()
        powers = search_powers(search_term="Pack Tactics", limit=5)
        power = powers[0]
        assert power.name == "Pack Tactics"
    finally:
        clean_power_index()


def test_all_powers_have_icons():
    for k, p in Powers.PowerLookup.items():
        assert p.icon_path is not None, f"Power {k} does not have an icon"

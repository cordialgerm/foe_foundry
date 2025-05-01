from foe_foundry_data.powers import clean_power_index, search_powers


def test_search_for_powers():
    try:
        clean_power_index()
        powers = search_powers(search_term="Pack Tactics", limit=1)
        power = powers[0]
        assert power.name == "Pack Tactics"
    finally:
        clean_power_index()

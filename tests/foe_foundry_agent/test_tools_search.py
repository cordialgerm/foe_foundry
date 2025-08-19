from foe_foundry_agent.tools import search


def test_search_monsters_basic():
    # Search for a well-known monster
    result = search.search_monsters("aboleth")
    assert "aboleth" in result.lower()
    assert "Monster Search Results" in result


def test_search_monsters_spell():
    # Search for monsters with the suggestion spell
    result = search.search_monsters("suggestion spell")
    assert "suggestion" in result.lower() or "spell" in result.lower()


def test_get_monster_detail_basic():
    # Try to get details for a well-known monster
    result = search.get_monster_detail("aboleth")
    assert "aboleth" in result.lower() or "No monster found" in result


def test_get_monster_detail_url():
    # Try to get details using a Foe Foundry URL format
    url = "https://foefoundry.com/monsters/aberration/#aboleth"
    result = search.get_monster_detail(url)
    assert "aboleth" in result.lower() or "No monster found" in result


def test_get_monster_detail_internal_url():
    # Try to get details using internal monster URL format
    url = "monster://aboleth"
    result = search.get_monster_detail(url)
    assert "aboleth" in result.lower() or "No monster found" in result

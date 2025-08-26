from foe_foundry_agent.tools import grep

# Sample test for grep_monster_markdown


def test_grep_monster_markdown_basic(tmp_path):
    # Test real data search for 'Armor Class' in monster markdown files
    # Test real data search for 'Armor Class' in monster markdown files
    results = grep.grep_monster_markdown("aboleth")
    assert len(results) >= 3


def test_grep_monster_markdown_regex(tmp_path):
    # Test for any creature with the 'suggestion' spell or an ability with the word 'charm' in it
    results = grep.grep_monster_markdown.invoke(
        input=dict(query=r"suggestion|charm", regex=True)
    )
    # At least one result should mention 'suggestion' or 'charm'
    lower = results.lower()
    assert "suggestion" in lower or "charm" in lower

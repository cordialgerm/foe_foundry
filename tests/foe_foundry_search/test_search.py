from foe_foundry_search.search import search_documents


def test_search():
    # Test that searching for "emerald" returns results (should find green dragons)
    emerald_results = [
        result.document for result in search_documents("emerald", limit=10)
    ]
    assert len(emerald_results) > 0, "Should find documents containing 'emerald'"

    # Test that searching for "warrior" returns results
    warrior_results = [
        result.document for result in search_documents("warrior", limit=10)
    ]
    assert len(warrior_results) > 0, "Should find documents containing 'warrior'"


def test_search_with_highlights():
    # Test the new SearchResult functionality
    results = list(search_documents("raging warrior", limit=5))
    assert len(results) > 0, "Should find documents containing 'raging warrior'"

    result = results[0]

    # Check that matched fields and terms are populated
    assert len(result.matched_fields) > 0, "Should have matched fields"
    assert len(result.matched_terms) > 0, "Should have matched terms"

    # For emerald search, should match in content
    assert "content" in result.matched_fields, "Should match in content field"
    assert any(term == "warrior" for field, term in result.matched_terms), (
        "Should match 'warrior' term"
    )

    # Should have highlighted content since it matched in content
    assert result.highlighted_match is not None, "Should have highlighted content"
    assert '<b class="match' in result.highlighted_match, (
        "Should contain highlight markup"
    )

from foe_foundry_search.search import (
    EntityType,
    search_documents,
    search_entities_with_graph_expansion,
)


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


def test_search_with_highlights_bandit():
    # Test the new SearchResult functionality
    results = list(search_documents("sneaky bandit", limit=5))
    assert len(results) > 0, "Should find documents containing 'sneaky bandit'"

    result = results[0]

    # Check that matched fields and terms are populated
    assert len(result.matched_fields) > 0, "Should have matched fields"
    assert len(result.matched_terms) > 0, "Should have matched terms"


def test_search_with_graph_expansion():
    """Test the search_entities_with_graph_expansion function."""

    # Test with a simple query
    query = "sneaky bandit"
    results = list(
        search_entities_with_graph_expansion(
            query,
            entity_types={EntityType.MONSTER, EntityType.FAMILY},
            limit=5,
            max_hops=2,
            alpha=0.15,
        )
    )

    print(f"\nFound {len(results)} results for query '{query}':")
    for i, result in enumerate(results):
        print(f"  {i + 1}. Score: {result.score:.3f}")
        if result.monster_key:
            print(f"     Monster: {result.monster_key}")
        if result.family_key:
            print(f"     Family: {result.family_key}")
        print(f"     Document matches: {len(result.document_matches)}")

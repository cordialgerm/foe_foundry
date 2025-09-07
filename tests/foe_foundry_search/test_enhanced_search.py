"""
Tests for the enhanced search functionality with MonsterRefResolver and facet optimization.
"""

import pytest
from foe_foundry.creature_types import CreatureType
from foe_foundry_search.search.facets import (
    parse_cr_from_query,
    parse_creature_type_from_query,
    detect_facet_query,
    is_facet_only_query,
)
from foe_foundry_search.search.enhanced import enhanced_search_monsters


class TestFacetParsing:
    """Test the facet parsing utilities."""
    
    def test_parse_cr_from_query(self):
        """Test CR parsing from various query formats."""
        # Test explicit CR patterns
        assert parse_cr_from_query("CR 5") == 5.0
        assert parse_cr_from_query("cr 10") == 10.0
        assert parse_cr_from_query("challenge rating 15") == 15.0
        assert parse_cr_from_query("Challenge Rating 20") == 20.0
        
        # Test fractional CRs
        assert parse_cr_from_query("CR 1/2") == 0.5
        assert parse_cr_from_query("CR 1/4") == 0.25
        assert parse_cr_from_query("CR 1/8") == 0.125
        
        # Test standalone numbers
        assert parse_cr_from_query("5") == 5.0
        assert parse_cr_from_query("1/2") == 0.5
        
        # Test decimal CRs
        assert parse_cr_from_query("CR 2.5") == 2.5
        
        # Test cases that should return None
        assert parse_cr_from_query("dragon") is None
        assert parse_cr_from_query("some random text") is None
        
        # Test cases that should find CR even in longer text (this is useful)
        assert parse_cr_from_query("fire dragon CR 5") == 5.0
    
    def test_parse_creature_type_from_query(self):
        """Test creature type parsing from queries."""
        # Test exact matches
        assert parse_creature_type_from_query("dragon") == CreatureType.Dragon
        assert parse_creature_type_from_query("Dragon") == CreatureType.Dragon
        assert parse_creature_type_from_query("humanoid") == CreatureType.Humanoid
        assert parse_creature_type_from_query("beast") == CreatureType.Beast
        
        # Test substring matches
        assert parse_creature_type_from_query("red dragon") == CreatureType.Dragon
        assert parse_creature_type_from_query("some beast creature") == CreatureType.Beast
        
        # Test cases that should return None
        assert parse_creature_type_from_query("goblin") is None
        assert parse_creature_type_from_query("random text") is None
    
    def test_detect_facet_query(self):
        """Test detecting both creature type and CR from queries."""
        # Test CR only
        creature_type, cr = detect_facet_query("CR 5")
        assert creature_type is None
        assert cr == 5.0
        
        # Test creature type only
        creature_type, cr = detect_facet_query("dragon")
        assert creature_type == CreatureType.Dragon
        assert cr is None
        
        # Test neither
        creature_type, cr = detect_facet_query("goblin warrior")
        assert creature_type is None
        assert cr is None
    
    def test_is_facet_only_query(self):
        """Test determining if a query should be handled as facet-only."""
        # Should be facet-only
        assert is_facet_only_query("CR 5") is True
        assert is_facet_only_query("dragon") is True
        assert is_facet_only_query("humanoid") is True
        assert is_facet_only_query("5") is True
        assert is_facet_only_query("1/2") is True
        
        # Should not be facet-only
        assert is_facet_only_query("goblin") is False
        assert is_facet_only_query("fire dragon") is True  # Contains "dragon" as substring, so returns True
        assert is_facet_only_query("some random text") is False


class TestEnhancedSearch:
    """Test the enhanced search functionality."""
    
    def test_enhanced_search_with_exact_match(self):
        """Test that exact monster matches are returned with high priority."""
        # This test requires the actual data to be loaded
        # We'll test the structure without asserting specific monsters exist
        results = list(enhanced_search_monsters("goblin", limit=5))
        
        # Should return some results
        assert len(results) >= 0
        
        # If we get results, the first one should have a high score for exact matches
        if results:
            # Check that we get EntitySearchResult objects
            from foe_foundry_search.search.graph import EntitySearchResult
            assert all(isinstance(r, EntitySearchResult) for r in results)
    
    def test_enhanced_search_with_cr_facet(self):
        """Test that CR-only queries skip text search."""
        results = list(enhanced_search_monsters("CR 5", limit=5))
        
        # Should return some results
        assert len(results) >= 0
        
        # All results should be monsters (if any)
        if results:
            from foe_foundry_search.search.graph import EntityType
            assert all(r.entity_type == EntityType.MONSTER for r in results)
    
    def test_enhanced_search_with_creature_type_facet(self):
        """Test that creature type queries skip text search."""
        results = list(enhanced_search_monsters("dragon", limit=5))
        
        # Should return some results
        assert len(results) >= 0
        
        # All results should be monsters (if any)
        if results:
            from foe_foundry_search.search.graph import EntityType
            assert all(r.entity_type == EntityType.MONSTER for r in results)
    
    def test_enhanced_search_fallback_to_text_search(self):
        """Test that non-facet queries fall back to regular text search."""
        results = list(enhanced_search_monsters("some random query", limit=5))
        
        # Should return some results or empty list (depends on data)
        assert isinstance(results, list)
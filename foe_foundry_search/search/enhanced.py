"""
Enhanced search functionality with MonsterRefResolver and facet optimization.
"""

from typing import Iterable, Set

import numpy as np

from foe_foundry.creature_types import CreatureType
from foe_foundry_data.monsters.all import Monsters
from foe_foundry_data.refs.monster_ref import MonsterRefResolver

from .facets import detect_facet_query, is_facet_only_query
from .graph import EntitySearchResult, EntityType, search_monsters

EXACT_MATCH_BOOST = 100.0


def enhanced_search_monsters(
    search_query: str,
    target_cr: float | None = None,
    min_cr: float | None = None,
    max_cr: float | None = None,
    creature_types: set[CreatureType] | None = None,
    limit: int = 10,
    max_hops: int = 3,
    alpha: float = 0.15,
) -> Iterable[EntitySearchResult]:
    """
    Enhanced monster search with performance optimizations:

    1. First checks for exact monster matches using MonsterRefResolver
    2. Then checks if query is a facet (creature type or CR) to avoid text search
    3. Falls back to regular text search if needed

    Args:
        search_query: The query to search for
        target_cr: Target challenge rating (backward compatibility)
        min_cr: Minimum challenge rating
        max_cr: Maximum challenge rating
        creature_types: Set of creature types to filter by
        limit: Maximum number of results to return
        max_hops: Maximum hops for graph traversal
        alpha: Decay factor for graph traversal

    Returns:
        Iterable of EntitySearchResult objects
    """

    # Handle empty or whitespace-only queries
    if not search_query or not search_query.strip():
        # If we have creature type filters or CR filters, treat as facet-only query
        if (
            creature_types
            or target_cr is not None
            or min_cr is not None
            or max_cr is not None
        ):
            return _get_facet_only_results(
                target_cr, min_cr, max_cr, creature_types or set(), limit
            )
        else:
            # No query and no filters - return empty results
            return []

    # Step 1: Check for exact monster match using MonsterRefResolver
    ref_resolver = MonsterRefResolver()
    monster_ref = ref_resolver.resolve_monster_ref(search_query)

    if monster_ref is not None and monster_ref.monster is not None:
        # We found an exact match! Return it with highest score
        exact_match_result = EntitySearchResult(
            id=f"exact_match_{monster_ref.monster.key}",
            entity_type=EntityType.MONSTER,
            monster_key=monster_ref.monster.key,
            power_key=None,
            family_key=None,
            score=1.2 * EXACT_MATCH_BOOST,  # Very high score to ensure it's first
            document_matches=[],
        )

        # Check if the exact match passes our filters
        if _passes_filters(
            monster_ref.monster, target_cr, min_cr, max_cr, creature_types
        ):
            # Return exact match plus additional results from normal search (up to limit)
            results = [exact_match_result]

            # Get additional results from normal search, excluding the exact match
            remaining_limit = max(0, limit - 1)
            if remaining_limit > 0:
                additional_results = _get_regular_search_results(
                    search_query,
                    target_cr,
                    min_cr,
                    max_cr,
                    creature_types,
                    remaining_limit,
                    max_hops,
                    alpha,
                    exclude_monster_key=monster_ref.monster.key,
                    template_boost_key=monster_ref.template.key,
                )
                results.extend(additional_results)

            return results

    # Step 2: Check if this is a facet-only query
    if is_facet_only_query(search_query):
        detected_creature_type, detected_cr = detect_facet_query(search_query)

        # Apply detected facets to our search parameters
        final_creature_types = creature_types or set()
        if detected_creature_type is not None:
            final_creature_types = {detected_creature_type} | final_creature_types

        final_target_cr = target_cr
        final_min_cr = min_cr
        final_max_cr = max_cr

        if detected_cr is not None:
            # Override CR parameters with detected CR
            final_target_cr = detected_cr
            final_min_cr = None
            final_max_cr = None

        # For facet-only queries, return all matching monsters without text search
        return _get_facet_only_results(
            final_target_cr, final_min_cr, final_max_cr, final_creature_types, limit
        )

    # Step 3: Fall back to regular text search
    return _get_regular_search_results(
        search_query, target_cr, min_cr, max_cr, creature_types, limit, max_hops, alpha
    )


def _passes_filters(
    monster,
    target_cr: float | None,
    min_cr: float | None,
    max_cr: float | None,
    creature_types: Set[CreatureType] | None,
) -> bool:
    """Check if a monster passes the CR and creature type filters."""

    # Check CR filtering
    if min_cr is not None or max_cr is not None:
        effective_min_cr = min_cr if min_cr is not None else 0.0
        effective_max_cr = max_cr if max_cr is not None else float("inf")
        if not (effective_min_cr <= monster.cr <= effective_max_cr):
            return False
    elif target_cr is not None:
        # Use target_cr logic
        if target_cr < 1:
            effective_min_cr = 0
            effective_max_cr = 1
        elif target_cr < 5:
            effective_min_cr = target_cr - 1
            effective_max_cr = target_cr + 1
        else:
            effective_min_cr = 0.75 * target_cr
            effective_max_cr = 1.25 * target_cr

        if not (effective_min_cr <= monster.cr <= effective_max_cr):
            return False

    # Check creature type filtering
    if creature_types is not None and len(creature_types) > 0:
        try:
            monster_creature_type = CreatureType.parse(monster.creature_type)
            if monster_creature_type not in creature_types:
                return False
        except (ValueError, AttributeError):
            return False

    return True


def _get_facet_only_results(
    target_cr: float | None,
    min_cr: float | None,
    max_cr: float | None,
    creature_types: Set[CreatureType],
    limit: int,
) -> list[EntitySearchResult]:
    """Get results based purely on facet filtering without text search."""

    results = []

    # Get all monsters and filter by facets
    all_monsters = Monsters.one_of_each_monster

    for monster in all_monsters:
        if len(results) >= limit:
            break

        if _passes_filters(monster, target_cr, min_cr, max_cr, creature_types):
            # Create a result with a moderate score (lower than exact matches)
            result = EntitySearchResult(
                id=f"facet_match_{monster.key}",
                entity_type=EntityType.MONSTER,
                monster_key=monster.key,
                power_key=None,
                family_key=None,
                score=10,  # standard score for facet matches
                document_matches=[],
            )
            results.append(result)

    return results


def _get_regular_search_results(
    search_query: str,
    target_cr: float | None,
    min_cr: float | None,
    max_cr: float | None,
    creature_types: Set[CreatureType] | None,
    limit: int,
    max_hops: int,
    alpha: float,
    exclude_monster_key: str | None = None,
    template_boost_key: str | None = None,
) -> list[EntitySearchResult]:
    """Get results using the regular text search approach."""

    results: list[EntitySearchResult] = []
    # Get extra results to account for boosting potentially changing the order
    search_limit = limit + (1 if exclude_monster_key else 0)
    if template_boost_key:
        # Get more results when boosting to ensure good variety after reordering
        search_limit = min(search_limit * 2, 100)

    for result in search_monsters(
        search_query=search_query,
        target_cr=target_cr,
        min_cr=min_cr,
        max_cr=max_cr,
        creature_types=creature_types,
        limit=search_limit,
        max_hops=max_hops,
        alpha=alpha,
    ):
        # Skip excluded monster if specified
        if exclude_monster_key and result.monster_key == exclude_monster_key:
            continue

        # Boost monsters from the same template if specified
        if template_boost_key and result.monster_key:
            from foe_foundry_data.monsters.all import Monsters

            monster = Monsters.lookup.get(result.monster_key)
            if monster and monster.template_key == template_boost_key:
                # Boost the score for monsters from the same template
                # Create a new EntitySearchResult with boosted score
                result = result.copy(
                    score=result.score + EXACT_MATCH_BOOST
                )  # Boost score for same template

        results.append(result)

    if not len(results):
        return []

    # Sort by score (descending)
    results.sort(key=lambda r: r.score, reverse=True)

    # Re-rank results to promote similar monsters to the top
    results = _rerank_results(results)

    # Selectively filter results to remove low-score outliers
    results = _selective_filter_results(results)

    return results[:limit]


def _rerank_results(results: list[EntitySearchResult]) -> list[EntitySearchResult]:
    high_score = results[0].score
    high_score_monster_key = results[0].monster_key
    high_score_monster = (
        Monsters.lookup.get(high_score_monster_key) if high_score_monster_key else None
    )
    high_score_family_keys = (
        set(high_score_monster.family_keys)
        if high_score_monster and high_score_monster.family_keys
        else set()
    )

    # Re-Rank results based on similarity to the top result
    reranked_results = [results[0]]
    if high_score_monster is not None:
        # boost any other results with the same template, families, or creature types
        for i, result in enumerate(results[1:], start=1):
            monster = (
                Monsters.lookup.get(result.monster_key) if result.monster_key else None
            )
            family_keys = (
                set(monster.family_keys) if monster and monster.family_keys else set()
            )

            if monster and monster.template_key == high_score_monster.template_key:
                boost = 1.75
            elif monster and any(family_keys.intersection(high_score_family_keys)):
                boost = 1.5
            elif monster and monster.creature_type == high_score_monster.creature_type:
                boost = 1.25
            else:
                boost = 1.0

            # Cap the boost to prevent changing the first place answer
            new_score = min(result.score * boost, (0.98**i) * high_score)

            # Boost the score for monsters from the same template
            # Create a new EntitySearchResult with boosted score
            reranked_result = result.copy(
                score=new_score
            )  # Boost score for same template
            reranked_results.append(reranked_result)

    # Sort by score (descending) and return top results
    reranked_results.sort(key=lambda r: r.score, reverse=True)
    return reranked_results


def _selective_filter_results(
    results: list[EntitySearchResult],
) -> list[EntitySearchResult]:
    """Filter results to only include those with a score >= 33% of the top score."""
    high_score = results[0].score

    if len(results) >= 3:
        return [r for r in results if r.score >= 0.4 * high_score]
    return results

"""
Graph-based entity search for Foe Foundry.

This module provides functionality to search for entities (monsters, families, powers)
using graph traversal with strength decay. The approach:

1. Start with document search results from the query
2. For each matching document, traverse the graph to find connected entities
3. Apply strength decay (alpha) at each hop to reduce influence over distance
4. Aggregate results and return ranked entities

Key functions:
- find_descendants_with_decay: Core graph traversal with decay
- search_entities_with_graph_expansion: Full search pipeline
- search_entities: Legacy wrapper (redirects to graph expansion)

Example usage:
    from foe_foundry_search.search import search_entities_with_graph_expansion, EntityType

    results = search_entities_with_graph_expansion(
        "dragon",
        entity_types={EntityType.MONSTER, EntityType.FAMILY},
        limit=10,
        max_hops=3,
        alpha=0.15
    )

    for result in results:
        print(f"Score: {result.score:.3f}")
        if result.monster_key:
            print(f"  Monster: {result.monster_key}")
        elif result.family_key:
            print(f"  Family: {result.family_key}")
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from enum import StrEnum
from typing import Callable, Iterable

from foe_foundry.creature_types import CreatureType

from ..graph import find_descendants_with_decay, load_graph
from .documents import DocType, DocumentSearchResult, search_documents


class EntityType(StrEnum):
    MONSTER = "monster"
    MONSTER_THIRD_PARTY = "monster_third_party"
    FAMILY = "family"
    POWER = "power"


@dataclass(kw_only=True)
class EntitySearchResult:
    id: str
    entity_type: EntityType
    monster_key: str | None
    power_key: str | None
    family_key: str | None

    score: float
    document_matches: list[DocumentSearchResult]

    def copy(self, **args) -> EntitySearchResult:
        return replace(self, **args)


def search_entities_with_graph_expansion(
    search_query: str,
    entity_types: set[EntityType] | None = None,
    limit: int = 5,
    max_hops: int = 3,
    alpha: float = 0.15,
    doc_type_weights: dict[DocType, float] | None = None,
    custom_filter: Callable[[dict], bool] | None = None,
) -> Iterable[EntitySearchResult]:
    """
    Search for entities using document search followed by graph expansion with strength decay.

    Args:
        search_query: The query to search for
        entity_types: Types of entities to find
        limit: Maximum number of results to return
        max_hops: Maximum hops for graph traversal
        alpha: Decay factor for graph traversal
    """
    if entity_types is None or len(entity_types) == 0:
        entity_types = {EntityType.MONSTER, EntityType.FAMILY, EntityType.POWER}

    # Map entity types to graph node types
    target_node_types = set()
    if EntityType.MONSTER in entity_types:
        target_node_types.add("FF_MON")
    if EntityType.MONSTER_THIRD_PARTY in entity_types:
        target_node_types.add("MON")
    if EntityType.FAMILY in entity_types:
        target_node_types.add("FF_FAM")
    if EntityType.POWER in entity_types:
        target_node_types.add("POW")

    # Search documents first
    doc_results = list(
        search_documents(
            search_query, limit=2 * limit, doc_type_weights=doc_type_weights
        )
    )

    # Collect all graph paths from document results
    all_paths = []
    for doc_result in doc_results:
        paths = find_descendants_with_decay(
            doc_result.document.doc_id,
            target_node_types,
            max_hops=max_hops,
            alpha=alpha,
            custom_filter=custom_filter,
        )
        all_paths.extend(paths)

    # Group paths by target node and calculate combined scores
    node_to_results = {}
    for path in all_paths:
        if path.target_node_id not in node_to_results:
            node_to_results[path.target_node_id] = {
                "paths": [],
                "total_strength": 0.0,
                "target_type": path.target_type,
            }

        node_to_results[path.target_node_id]["paths"].append(path)
        node_to_results[path.target_node_id]["total_strength"] += path.strength

    # Convert to EntitySearchResult objects
    graph = load_graph()
    results = []

    for node_id, data in node_to_results.items():
        node_data = graph.nodes[node_id]

        # Extract relevant keys based on node type
        monster_key = node_data.get("monster_key")
        power_key = node_data.get("power_key")
        family_key = node_data.get("family_key")

        # Find corresponding document matches for the paths
        document_matches = []
        for path in data["paths"]:
            # Find the document result that led to this path
            for doc_result in doc_results:
                if doc_result.document.doc_id == path.source_doc_id:
                    document_matches.append(doc_result)
                    break

        node_type = node_data["type"]
        if node_type == "FF_MON":
            entity_type = EntityType.MONSTER
        elif node_type == "MON":
            entity_type = EntityType.MONSTER_THIRD_PARTY
        elif node_type == "FF_FAM":
            entity_type = EntityType.FAMILY
        elif node_type == "POW":
            entity_type = EntityType.POWER
        else:
            raise ValueError(f"Unknown node type: {node_type}")

        results.append(
            EntitySearchResult(
                id=node_id,
                entity_type=entity_type,
                monster_key=monster_key,
                power_key=power_key,
                family_key=family_key,
                score=data["total_strength"],
                document_matches=document_matches,
            )
        )

    # Sort by score (descending) and limit results
    results.sort(key=lambda x: x.score, reverse=True)
    return results[:limit]


def search_monsters(
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
    Search for monsters using document search followed by graph expansion with strength decay.
    """

    # We want to be sure the noisier document types are weighted lower
    doc_type_weights = {
        DocType.monster_ff: 3.0,  # boost official monsters highest
        DocType.monster_other: 1.5,
        DocType.power_ff: 1.0,
        DocType.blog_post: 0.5,  # might just mention the search term in passing
    }

    # custom node-level filter based on monster parameters
    def custom_filter(node: dict) -> bool:
        if node["type"] != "FF_MON":
            return False

        cr: float | None = node.get("cr")
        if cr is None:
            return False

        # Handle CR filtering with precedence: min_cr/max_cr over target_cr
        if min_cr is not None or max_cr is not None:
            # Use explicit min/max CR if provided
            effective_min_cr = min_cr if min_cr is not None else 0.0
            effective_max_cr = max_cr if max_cr is not None else float("inf")

            if not (effective_min_cr <= cr <= effective_max_cr):
                return False
        elif target_cr is not None:
            # Fall back to target_cr logic for backward compatibility
            if target_cr < 1:
                effective_min_cr = 0
                effective_max_cr = 1
            elif target_cr < 5:
                effective_min_cr = target_cr - 1
                effective_max_cr = target_cr + 1
            else:
                effective_min_cr = 0.75 * target_cr
                effective_max_cr = 1.25 * target_cr

            if not (effective_min_cr <= cr <= effective_max_cr):
                return False

        node_creature_type = node.get("creature_type")
        node_creature_type = (
            CreatureType.parse(node_creature_type) if node_creature_type else None
        )
        if creature_types is not None and node_creature_type not in creature_types:
            return False

        return True

    return search_entities_with_graph_expansion(
        search_query,
        entity_types={EntityType.MONSTER},
        limit=limit,
        max_hops=max_hops,
        custom_filter=custom_filter,
        alpha=alpha,
        doc_type_weights=doc_type_weights,
    )


def search_powers(
    search_query: str,
    limit: int = 10,
    max_hops: int = 3,
    alpha: float = 0.15,
) -> Iterable[EntitySearchResult]:
    """
    Search for powers using document search followed by graph expansion with strength decay.

    Args:
        search_query: The query to search for
        limit: Maximum number of results to return
        max_hops: Maximum hops for graph traversal
        alpha: Decay factor for graph traversal
    """
    return search_entities_with_graph_expansion(
        search_query,
        entity_types={EntityType.POWER},
        limit=limit,
        max_hops=max_hops,
        alpha=alpha,
    )

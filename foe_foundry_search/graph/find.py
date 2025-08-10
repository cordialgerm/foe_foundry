from collections import deque
from dataclasses import dataclass

from ..graph import load_graph


@dataclass(kw_only=True)
class GraphPath:
    """Represents a path from a source document to a target node with decayed strength."""

    source_doc_id: str
    target_node_id: str
    target_type: str
    path: list[str]  # List of node IDs in the path
    strength: float  # Decayed strength based on alpha and hop count
    hops: int


def find_descendants_with_decay(
    document_doc_id: str, target_types: set[str], max_hops: int = 3, alpha: float = 0.15
) -> list[GraphPath]:
    """
    Find all nodes of the desired types that are descendants of a document up to N hops,
    with strength decay along each hop.

    Args:
        document_doc_id: The document ID to start from
        target_types: Set of node types to find (e.g., {'FF_MON', 'FF_FAM', 'POW'})
        max_hops: Maximum number of hops to traverse
        alpha: Decay factor applied at each hop (default 0.15)

    Returns:
        List of GraphPath objects representing paths to target nodes with decayed strength
    """
    graph = load_graph()
    source_node_id = f"DOC:{document_doc_id}"

    if not graph.has_node(source_node_id):
        return []

    paths = []

    # BFS with path tracking and strength decay
    queue = deque(
        [(source_node_id, [source_node_id], 1.0, 0)]
    )  # (node_id, path, strength, hops)
    visited = set()

    while queue:
        current_node, path, strength, hops = queue.popleft()

        # Skip if we've already visited this node with equal or better strength
        state_key = (current_node, hops)
        if state_key in visited:
            continue
        visited.add(state_key)

        # If this is a target node type and not the source, add to results
        if (
            current_node != source_node_id
            and graph.nodes[current_node]["type"] in target_types
        ):
            paths.append(
                GraphPath(
                    source_doc_id=document_doc_id,
                    target_node_id=current_node,
                    target_type=graph.nodes[current_node]["type"],
                    path=path.copy(),
                    strength=strength,
                    hops=hops,
                )
            )

        # Continue traversal if we haven't reached max hops
        if hops < max_hops:
            for neighbor in graph.successors(current_node):
                new_strength = strength * (1 - alpha)  # Apply decay
                new_path = path + [neighbor]
                queue.append((neighbor, new_path, new_strength, hops + 1))

    return paths

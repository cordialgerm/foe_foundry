from dataclasses import dataclass

import networkx as nx

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

    # Get the ego graph (subgraph of all nodes within max_hops radius)
    ego_subgraph = nx.ego_graph(graph, source_node_id, radius=max_hops)

    # Get distances from source to all nodes in the ego graph
    distances = nx.single_source_shortest_path_length(ego_subgraph, source_node_id)

    # Get the actual paths for nodes we need
    shortest_paths = nx.single_source_shortest_path(ego_subgraph, source_node_id)

    paths = []
    for target_node, distance in distances.items():
        # Skip the source node itself
        if target_node == source_node_id:
            continue

        # Only include nodes of target types
        if graph.nodes[target_node]["type"] in target_types:
            # Calculate strength with decay
            strength = (1 - alpha) ** distance

            paths.append(
                GraphPath(
                    source_doc_id=document_doc_id,
                    target_node_id=target_node,
                    target_type=graph.nodes[target_node]["type"],
                    path=shortest_paths[target_node],
                    strength=strength,
                    hops=distance,
                )
            )

    return paths

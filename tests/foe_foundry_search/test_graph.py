"""
Test module for graph operations in Foe Foundry Search.

This module contains tests for graph construction, visualization, and subgraph sampling.
It includes the logic previously in __main__.py for testing purposes.
"""

import random
from pathlib import Path

import networkx as nx

from foe_foundry_search.graph import (
    find_descendants_with_decay,
    load_graph,
    rebuild_graph,
    visualize_all_layouts,
)


def sample_subgraph(G, max_mon_nodes: int = 10, ego_radius: int = 4) -> nx.DiGraph:
    """
    Sample a subgraph from the full graph for visualization and testing.

    Args:
        G: The full NetworkX graph
        max_mon_nodes: Maximum number of MON nodes to sample
        ego_radius: Radius for ego graph expansion

    Returns:
        A subgraph containing the sampled nodes and their connections
    """
    # Get all MON nodes whose names start with 'a' or 'b'
    mon_nodes = [n for n, d in G.nodes(data=True) if d.get("type") == "MON"]
    sample_size = min(max_mon_nodes, len(mon_nodes))
    sampled_mons = random.sample(mon_nodes, sample_size)

    # Find all nodes up to ego_radius degree connection from sampled_mons using ego_graph
    nodes_to_plot = set()
    for node in sampled_mons:
        # ego_graph returns subgraph of all nodes within radius distance from node
        ego = nx.ego_graph(G.to_undirected(), node, radius=ego_radius)
        nodes_to_plot.update(ego.nodes())

    return G.subgraph(nodes_to_plot)


def test_graph_construction():
    """Test the basic graph construction functionality."""
    G = rebuild_graph()

    # Basic assertions about the graph
    assert isinstance(G, nx.DiGraph), "Graph should be a directed graph"
    assert G.number_of_nodes() > 0, "Graph should have nodes"

    print(
        f"Graph constructed with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges."
    )


def test_subgraph_sampling():
    """Test the subgraph sampling functionality."""
    G = load_graph()

    # Test with default parameters
    subgraph = sample_subgraph(G)
    assert isinstance(subgraph, nx.DiGraph), "Subgraph should be a directed graph"
    assert subgraph.number_of_nodes() <= G.number_of_nodes(), (
        "Subgraph should be smaller than or equal to original"
    )

    # Test with custom parameters
    small_subgraph = sample_subgraph(G, max_mon_nodes=10, ego_radius=2)
    assert isinstance(small_subgraph, nx.DiGraph), (
        "Small subgraph should be a directed graph"
    )


def test_visualization_layouts():
    """Test visualization with different layouts (without saving files)."""
    G = load_graph()
    subgraph = sample_subgraph(G)
    output_dir = Path.cwd() / "tests" / "outputs"
    output_dir.mkdir(exist_ok=True)
    visualize_all_layouts(subgraph, output_dir)


def test_find_descendants():
    """Test the find_descendants_with_decay function."""
    print("Testing find_descendants_with_decay...")

    # We need to find a real document ID to test with
    from foe_foundry_search.documents import iter_documents

    # Get the first few documents
    doc = next(d for d in iter_documents())

    print(f"Testing with document: {doc.doc_id} - {doc.name}")

    # Find descendants
    target_types = {"FF_MON", "FF_FAM", "POW"}
    paths = find_descendants_with_decay(doc.doc_id, target_types, max_hops=2)

    print(f"Found {len(paths)} paths:")
    for i, path in enumerate(paths[:5]):  # Show first 5
        print(f"  {i + 1}. {path.target_type} {path.target_node_id}")
        print(f"     Strength: {path.strength:.3f}, Hops: {path.hops}")
        print(f"     Path: {' -> '.join(path.path)}")

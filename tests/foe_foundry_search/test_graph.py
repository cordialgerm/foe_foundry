"""
Test module for graph operations in Foe Foundry Search.

This module contains tests for graph construction, visualization, and subgraph sampling.
It includes the logic previously in __main__.py for testing purposes.
"""

import random
from pathlib import Path

import networkx as nx

from foe_foundry_search.graph import build_graph, visualize_all_layouts


def sample_subgraph(G, max_mon_nodes: int = 40, ego_radius: int = 4) -> nx.DiGraph:
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
    mon_nodes = [
        n
        for n, d in G.nodes(data=True)
        if d.get("type") == "MON" and d.get("name", "").lower().startswith(("a", "b"))
    ]
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
    G, issues = build_graph()

    # Basic assertions about the graph
    assert isinstance(G, nx.DiGraph), "Graph should be a directed graph"
    assert G.number_of_nodes() > 0, "Graph should have nodes"
    assert isinstance(issues, list), "Issues should be a list"

    print(
        f"Graph constructed with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges."
    )
    print(f"{len(issues)} issues found")
    for issue in issues:
        print(issue)


def test_subgraph_sampling():
    """Test the subgraph sampling functionality."""
    G, _ = build_graph()

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
    G, _ = build_graph()
    output_dir = Path.cwd() / "tests" / "outputs"
    output_dir.mkdir(exist_ok=True)
    visualize_all_layouts(G, output_dir)

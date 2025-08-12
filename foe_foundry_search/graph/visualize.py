from enum import Enum
from pathlib import Path

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np


class LayoutType(Enum):
    """Enumeration of available graph layout algorithms."""

    SPRING = "spring"
    KAMADA_KAWAI = "kamada_kawai"


def _create_layout_positions(subgraph: nx.DiGraph, layout_type: LayoutType) -> dict:
    """
    Generate node positions based on the specified layout algorithm.

    Args:
        subgraph: The NetworkX graph to layout
        layout_type: The layout algorithm to use

    Returns:
        Dictionary mapping node IDs to (x, y) positions
    """
    H = nx.Graph(subgraph)

    if layout_type == LayoutType.SPRING:
        return nx.spring_layout(H, seed=42, k=None, iterations=100)

    elif layout_type == LayoutType.KAMADA_KAWAI:
        seed_pos = nx.spring_layout(H, seed=42, k=None, iterations=100)
        rand_pos = nx.random_layout(H, seed=42)
        alpha = 0.8  # 0 = pure random, 1 = pure spring
        blend_pos = {
            n: alpha * np.array(seed_pos[n]) + (1 - alpha) * np.array(rand_pos[n])
            for n in H.nodes()
        }
        return nx.kamada_kawai_layout(
            nx.Graph(subgraph),
            weight=None,  # type: ignore
            scale=3.5,
            pos=blend_pos,
        )
    else:
        raise ValueError(f"Unsupported layout type: {layout_type}")


def visualize_graph(
    subgraph, output_dir: Path, layout_type: LayoutType = LayoutType.SPRING
):
    """
    Visualize a sampled subset of the graph with the specified layout.

    Args:
        subgraph: The sampled NetworkX graph
        layout_type: The layout algorithm to use for positioning nodes
    """
    plt.figure(figsize=(12, 8))
    pos = _create_layout_positions(subgraph, layout_type)

    # Priority order for drawing: FF_FAM, FF_MON, MON (srd), MON (not srd), DOC, POW
    priority = {
        "FF_FAM": 0,
        "FF_MON": 1,
        "MON_SRD": 2,
        "MON": 3,
        "DOC": 4,
        "POW": 5,
    }

    def node_priority(n):
        node = subgraph.nodes[n]
        t = str(node.get("type", ""))
        if t == "MON":
            return priority["MON_SRD"] if node.get("is_srd", False) else priority["MON"]
        return priority[t] if t in priority else 99

    sorted_nodes = sorted(subgraph.nodes, key=node_priority)

    # Prepare node attributes
    node_colors = {}
    node_sizes = {}
    labels = {}
    for n in subgraph.nodes:
        node_type = subgraph.nodes[n]["type"]
        if node_type == "DOC":
            node_colors[n] = "#1f77b4"
            node_sizes[n] = 5
            # No label for DOC nodes
        elif node_type == "FF_MON":
            node_colors[n] = "#8B0000"  # dark red
            node_sizes[n] = 20
            # Label is just the key, e.g. 'wolf' for 'FF_MON:wolf'
            labels[n] = n.split(":", 1)[-1]
        elif node_type == "FF_FAM":
            node_colors[n] = "#FFB6B6"  # light red
            node_sizes[n] = 20
            labels[n] = subgraph.nodes[n].get("family_key", n)
        elif node_type == "POW":
            node_colors[n] = "#800080"  # purple
            node_sizes[n] = 10
            # No label for POW nodes
        elif node_type == "MON":
            is_srd = subgraph.nodes[n].get("is_srd", False)
            node_colors[n] = "#2ca02c" if is_srd else "#ff7f0e"
            node_sizes[n] = 15 if is_srd else 12
            # no label for MON nodes
        else:
            node_colors[n] = "#cccccc"
            node_sizes[n] = 10

    # Draw DOC and POW nodes first (lowest layer)
    for t in ["DOC", "POW"]:
        nodes = [n for n in sorted_nodes if subgraph.nodes[n]["type"] == t]
        nx.draw_networkx_nodes(
            subgraph,
            pos,
            nodelist=nodes,
            node_color=[node_colors[n] for n in nodes],
            node_size=[node_sizes[n] for n in nodes],
            alpha=0.7,
            label=t,
        )

    # Draw MON (not srd), MON (srd), FF_MON, FF_FAM in order
    for t in ["MON", "FF_MON", "FF_FAM"]:
        if t == "MON":
            # Draw MON (not srd) first, then MON (srd)
            mon_nodes = [
                n
                for n in sorted_nodes
                if subgraph.nodes[n]["type"] == "MON"
                and not subgraph.nodes[n].get("is_srd", False)
            ]
            srd_nodes = [
                n
                for n in sorted_nodes
                if subgraph.nodes[n]["type"] == "MON"
                and subgraph.nodes[n].get("is_srd", False)
            ]
            nx.draw_networkx_nodes(
                subgraph,
                pos,
                nodelist=mon_nodes,
                node_color=[node_colors[n] for n in mon_nodes],
                node_size=[node_sizes[n] for n in mon_nodes],
                alpha=0.7,
                label="MON",
            )
            nx.draw_networkx_nodes(
                subgraph,
                pos,
                nodelist=srd_nodes,
                node_color=[node_colors[n] for n in srd_nodes],
                node_size=[node_sizes[n] for n in srd_nodes],
                alpha=0.8,
                label="MON_SRD",
            )
        else:
            nodes = [n for n in sorted_nodes if subgraph.nodes[n]["type"] == t]
            nx.draw_networkx_nodes(
                subgraph,
                pos,
                nodelist=nodes,
                node_color=[node_colors[n] for n in nodes],
                node_size=[node_sizes[n] for n in nodes],
                alpha=0.9,
                label=t,
            )

    # Draw edges
    nx.draw_networkx_edges(subgraph, pos, alpha=0.25, arrows=False)

    # Draw labels
    nx.draw_networkx_labels(
        subgraph,
        pos,
        labels=labels,
        font_size=8,
    )

    plt.title(f"Sampled Foe Foundry GraphRAG ({layout_type.value} layout)")
    plt.tight_layout()
    out_path = output_dir / f"graph_{layout_type.value}.png"
    plt.savefig(out_path, dpi=300)
    print(f"Sampled graph visualization saved to {out_path}")


def visualize_all_layouts(G, output_dir: Path):
    """
    Generate visualizations for all available layout types.

    Args:
        G: The full NetworkX graph
    """
    for layout_type in LayoutType:
        print(f"Generating visualization with {layout_type.value} layout...")
        visualize_graph(G, output_dir, layout_type)
        plt.close()  # Close the figure to free memory

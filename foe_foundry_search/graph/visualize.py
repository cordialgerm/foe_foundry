import os
import random
from enum import Enum

import matplotlib.pyplot as plt
import networkx as nx


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
    if layout_type == LayoutType.SPRING:
        return nx.spring_layout(subgraph, seed=42, k=None)

    elif layout_type == LayoutType.KAMADA_KAWAI:
        return nx.kamada_kawai_layout(subgraph)

    else:
        raise ValueError(f"Unsupported layout type: {layout_type}")


def visualize_graph_sampled(G, layout_type: LayoutType = LayoutType.SPRING):
    """
    Visualize a sampled subset of the graph with the specified layout.

    Args:
        G: The full NetworkX graph
        layout_type: The layout algorithm to use for positioning nodes
    """
    # Get all MON nodes whose names start with 'a' or 'b'
    mon_nodes = [
        n
        for n, d in G.nodes(data=True)
        if d.get("type") == "MON" and d.get("name", "").lower().startswith(("a", "b"))
    ]
    sample_size = min(40, len(mon_nodes))
    sampled_mons = random.sample(mon_nodes, sample_size)
    # Collect all 1st and 2nd degree neighbors of the sampled MON nodes
    nodes_to_plot = set(sampled_mons)
    # 1st degree: all nodes directly connected to sampled MONs (in or out)
    for mon in sampled_mons:
        nodes_to_plot.update(G.predecessors(mon))
        nodes_to_plot.update(G.successors(mon))
    # 2nd degree: all nodes connected to those neighbors
    first_degree = set(nodes_to_plot)
    for n1 in first_degree:
        nodes_to_plot.update(G.predecessors(n1))
        nodes_to_plot.update(G.successors(n1))

    # Add all FF_MON nodes connected to the MON nodes we have so far
    ff_mon_nodes = set()
    for mon in nodes_to_plot:
        if G.nodes[mon].get("type") == "MON":
            # Find FF_MON nodes connected to this MON node
            for pred in G.predecessors(mon):
                if G.nodes[pred].get("type") == "FF_MON":
                    ff_mon_nodes.add(pred)
            for succ in G.successors(mon):
                if G.nodes[succ].get("type") == "FF_MON":
                    ff_mon_nodes.add(succ)
    nodes_to_plot.update(ff_mon_nodes)

    # Add all FF_FAM nodes connected to the FF_MON nodes we have so far
    ff_fam_nodes = set()
    for ff_mon in ff_mon_nodes:
        for pred in G.predecessors(ff_mon):
            if G.nodes[pred].get("type") == "FF_FAM":
                ff_fam_nodes.add(pred)
        for succ in G.successors(ff_mon):
            if G.nodes[succ].get("type") == "FF_FAM":
                ff_fam_nodes.add(succ)
    nodes_to_plot.update(ff_fam_nodes)

    # Add all DOC nodes connected to the MON nodes we have so far
    doc_nodes = set()
    for mon in nodes_to_plot:
        if G.nodes[mon].get("type") == "MON":
            for pred in G.predecessors(mon):
                if G.nodes[pred].get("type") == "DOC":
                    doc_nodes.add(pred)
            for succ in G.successors(mon):
                if G.nodes[succ].get("type") == "DOC":
                    doc_nodes.add(succ)
    nodes_to_plot.update(doc_nodes)
    # Add all POW nodes connected to the FF_MON nodes we have so far
    pow_nodes = set()
    for ff_mon in ff_mon_nodes:
        for pred in G.predecessors(ff_mon):
            if G.nodes[pred].get("type") == "POW":
                pow_nodes.add(pred)
        for succ in G.successors(ff_mon):
            if G.nodes[succ].get("type") == "POW":
                pow_nodes.add(succ)
    nodes_to_plot.update(pow_nodes)
    subgraph = G.subgraph(nodes_to_plot)

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
    mon_labels = {}
    for n in subgraph.nodes:
        node_type = subgraph.nodes[n]["type"]
        if node_type == "DOC":
            node_colors[n] = "#1f77b4"
            node_sizes[n] = 5
            # No label for DOC nodes
        elif node_type == "FF_MON":
            node_colors[n] = "#8B0000"  # dark red
            node_sizes[n] = 120
            # Label is just the key, e.g. 'wolf' for 'FF_MON:wolf'
            labels[n] = n.split(":", 1)[-1]
        elif node_type == "FF_FAM":
            node_colors[n] = "#FFB6B6"  # light red
            node_sizes[n] = 150
            labels[n] = subgraph.nodes[n].get("family_key", n)
        elif node_type == "POW":
            node_colors[n] = "#800080"  # purple
            node_sizes[n] = 10
            # No label for POW nodes
        elif node_type == "MON":
            is_srd = subgraph.nodes[n].get("is_srd", False)
            node_colors[n] = "#2ca02c" if is_srd else "#ff7f0e"
            node_sizes[n] = 100 if is_srd else 80
            labels[n] = subgraph.nodes[n].get("name", n)
            mon_labels[n] = labels[n]
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
    nx.draw_networkx_edges(subgraph, pos, alpha=0.2)

    # Draw labels for FF_FAM, FF_MON, MON nodes only
    ff_fam_nodes = [n for n in labels if subgraph.nodes[n]["type"] == "FF_FAM"]
    ff_mon_nodes = [n for n in labels if subgraph.nodes[n]["type"] == "FF_MON"]
    mon_nodes = [n for n in labels if subgraph.nodes[n]["type"] == "MON"]

    # FF_FAM and FF_MON labels (font size 8)
    nx.draw_networkx_labels(
        subgraph,
        pos,
        labels={n: labels[n] for n in ff_fam_nodes + ff_mon_nodes},
        font_size=8,
    )
    # MON labels (smaller font size, e.g. 6)
    nx.draw_networkx_labels(
        subgraph,
        pos,
        labels={n: mon_labels[n] for n in mon_nodes},
        font_size=6,
    )

    plt.title(f"Sampled Foe Foundry GraphRAG ({layout_type.value} layout)")
    plt.tight_layout()
    out_path = os.path.join(os.path.dirname(__file__), f"graph_{layout_type.value}.png")
    plt.savefig(out_path, dpi=300)
    print(f"Sampled graph visualization saved to {out_path}")


def visualize_all_layouts(G):
    """
    Generate visualizations for all available layout types.

    Args:
        G: The full NetworkX graph
    """
    for layout_type in LayoutType:
        print(f"Generating visualization with {layout_type.value} layout...")
        visualize_graph_sampled(G, layout_type)
        plt.close()  # Close the figure to free memory

"""
Initial implementation of GraphRAG graph construction for Foe Foundry.
Builds a NetworkX graph with DOC and MON nodes and relevant edges.
"""

import json
import os

import networkx as nx

from foe_foundry.utils import name_to_key
from foe_foundry_search.documents import (
    iter_monster_docs,
    load_monster_doc_metas,
)

# Path to SRD mapping file
SRD_MAPPING_PATH = os.path.join(os.path.dirname(__file__), "monster_to_srd_a_b.json")


def build_graph():
    G = nx.DiGraph()

    # 1. Extract DOC nodes (MonsterDocument)
    for doc in iter_monster_docs():
        node_id = f"DOC:{doc.doc_id}"
        G.add_node(
            node_id, type="DOC", monster_key=doc.monster_key, id=node_id, text=doc.text
        )

    # 2. Extract MON nodes (MonsterDocumentMeta)
    metas = load_monster_doc_metas()  # dict[str, MonsterDocumentMeta]
    for key, meta in metas.items():
        node_id = f"MON:{key}"
        G.add_node(
            node_id,
            type="MON",
            id=key,
            name=meta.name,
            is_srd=meta.srd,
            text=meta.description,
        )

    # 3. Create DOC → MON edges (if document text mentions monster name)
    for doc in iter_monster_docs():
        if doc.monster_key not in metas:
            print(
                f"Warning: Document {doc.doc_id} references unknown monster {doc.monster_key}"
            )
            continue

        monster = metas[doc.monster_key]
        G.add_edge(
            f"DOC:{doc.doc_id}",
            f"MON:{monster.key}",
            type="about",
            relevancy=1.0,
        )

    # 4. Create MON → MON edges using SRD mappings
    if os.path.exists(SRD_MAPPING_PATH):
        with open(SRD_MAPPING_PATH, "r") as f:
            srd_map = json.load(f)
        for monster_name, srd_names in srd_map.items():
            if srd_names is None:
                continue

            monster_key = name_to_key(monster_name)

            for srd_name in srd_names:
                srd_monster_key = name_to_key(srd_name)

                # skip self references, we know SRD monsters reference themselves
                if srd_monster_key == monster_key:
                    continue

                mon_node_id = f"MON:{monster_key}"
                srd_node_id = f"MON:{srd_monster_key}"
                if G.has_node(mon_node_id) and G.has_node(srd_node_id):
                    G.add_edge(mon_node_id, srd_node_id, type="similar")

    return G


def main():
    G = build_graph()
    print(
        f"Graph constructed with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges."
    )

    # Visualization: sample 40 MON nodes and plot their 1st and 2nd degree neighbors
    try:
        import random

        import matplotlib.pyplot as plt

        # Get all MON nodes whose names start with 'a' or 'b'
        mon_nodes = [
            n
            for n, d in G.nodes(data=True)
            if d.get("type") == "MON"
            and d.get("name", "").lower().startswith(("a", "b"))
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
        subgraph = G.subgraph(nodes_to_plot)

        plt.figure(figsize=(12, 8))
        pos = nx.spring_layout(subgraph, seed=42)
        node_colors = []
        node_sizes = []
        labels = {}
        for n in subgraph.nodes:
            node_type = subgraph.nodes[n]["type"]
            if node_type == "DOC":
                node_colors.append("#1f77b4")
                node_sizes.append(50)
                # No label for DOC nodes
            else:
                is_srd = subgraph.nodes[n].get("is_srd", False)
                node_colors.append("#2ca02c" if is_srd else "#ff7f0e")
                node_sizes.append(300)
                labels[n] = subgraph.nodes[n].get("name", n)
        nx.draw(
            subgraph,
            pos,
            with_labels=False,
            node_color=node_colors,
            font_size=8,
            node_size=node_sizes,
        )
        # Draw labels only for MON nodes
        nx.draw_networkx_labels(
            subgraph,
            pos,
            labels=labels,
            font_size=8,
        )
        plt.title(
            "Sampled Foe Foundry GraphRAG: 40 MONs (A/B) + 1st/2nd Degree Neighbors"
        )
        plt.tight_layout()
        out_path = os.path.join(
            os.path.dirname(__file__), "foe_foundry_graph_sampled.png"
        )
        plt.savefig(out_path)
        print(f"Sampled graph visualization saved to {out_path}")
    except ImportError:
        print("matplotlib not installed; skipping visualization.")


if __name__ == "__main__":
    main()

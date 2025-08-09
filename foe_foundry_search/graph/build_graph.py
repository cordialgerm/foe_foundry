"""
Initial implementation of GraphRAG graph construction for Foe Foundry.
Builds a NetworkX graph with DOC and MON nodes and relevant edges.
"""

import json
import os

import networkx as nx

from foe_foundry.creatures import AllTemplates
from foe_foundry.utils import name_to_key
from foe_foundry_data.families import load_families
from foe_foundry_search.documents import (
    iter_monster_docs,
    load_monster_doc_metas,
)

# Path to SRD mapping file
SRD_MAPPING_PATH = os.path.join(os.path.dirname(__file__), "monster_to_srd_a_b.json")


def build_graph():
    G = nx.DiGraph()

    issues = []

    # Extract DOC nodes (MonsterDocument)
    for doc in iter_monster_docs():
        node_id = f"DOC:{doc.doc_id}"
        G.add_node(
            node_id, type="DOC", monster_key=doc.monster_key, id=node_id, text=doc.text
        )

    # Extract MON nodes (MonsterDocumentMeta)
    metas = load_monster_doc_metas()  # dict[str, MonsterDocumentMeta]
    for key, meta in metas.items():
        node_id = f"MON:{key}"
        G.add_node(
            node_id,
            type="MON",
            id=key,
            name=meta.name,
            is_srd=meta.srd,
            description=meta.description,
        )

    # Create DOC → MON edges
    for doc in iter_monster_docs():
        if doc.monster_key not in metas:
            issues.append(
                f"Document {doc.doc_id} references unknown monster {doc.monster_key}"
            )
            continue

        monster = metas[doc.monster_key]
        G.add_edge(
            f"DOC:{doc.doc_id}",
            f"MON:{monster.key}",
            type="about",
            relevancy=1.0,
        )

    # Create MON → MON edges using SRD mappings
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
                else:
                    if not G.has_node(mon_node_id):
                        issues.append(
                            f"SRD mapping {monster_name} → {srd_name} references unknown other monster {monster_key}"
                        )
                    if not G.has_node(srd_node_id):
                        issues.append(
                            f"SRD mapping {monster_name} → {srd_name} references unknown SRD monster {srd_monster_key}"
                        )

    # Add FF_MON nodes
    for template in AllTemplates:
        for variant in template.variants:
            for monster in variant.monsters:
                node_id = f"FF_MON:{monster.key}"
                G.add_node(
                    node_id,
                    type="FF_MON",
                    monster_key=monster.key,
                    template_key=template.key,
                )

                for srd_creature in monster.srd_creatures or []:
                    srd_monster_key = name_to_key(srd_creature)
                    srd_node_id = f"MON:{srd_monster_key}"

                    if G.has_node(srd_node_id):
                        G.add_edge(node_id, srd_node_id, type="implemented")
                    else:
                        issues.append(
                            f"FF_MON {monster.key} references unknown SRD creature {srd_creature}"
                        )

                for other_monster_name, _ in (monster.other_creatures or {}).items():
                    other_monster_key = name_to_key(other_monster_name)
                    other_node_id = f"MON:{other_monster_key}"

                    if G.has_node(other_node_id):
                        G.add_edge(node_id, other_node_id, type="implemented")
                    else:
                        issues.append(
                            f"FF_MON {monster.key} references unknown other creature {other_monster_name}"
                        )

    # Add FF_FAM nodes
    for family in load_families():
        node_id = f"FF_FAM:{family.key}"
        G.add_node(
            node_id,
            type="FF_FAM",
            family_key=family.key,
        )

        for monster in family.monsters:
            monster_node_id = f"FF_MON:{monster.key}"
            if G.has_node(monster_node_id):
                G.add_edge(node_id, monster_node_id, type="member")
            else:
                issues.append(
                    f"FF_FAM {family.key} references unknown FF_MON {monster.key}"
                )

    return G, issues


def main():
    G, issues = build_graph()

    print(
        f"Graph constructed with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges."
    )

    print(f"{len(issues)} issues found")
    for issue in issues:
        print(issue)

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
            elif node_type == "FF_MON":
                node_colors.append("#8B0000")  # dark red
                node_sizes.append(300)
                labels[n] = subgraph.nodes[n].get("name", n)
            elif node_type == "FF_FAM":
                node_colors.append("#FFB6B6")  # light red
                node_sizes.append(400)
                labels[n] = subgraph.nodes[n].get("family_key", n)
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

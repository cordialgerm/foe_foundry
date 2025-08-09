"""
Initial implementation of GraphRAG graph construction for Foe Foundry.
Builds a NetworkX graph with DOC and MON nodes and relevant edges.
"""

import json
import os

import dotenv
import networkx as nx

from foe_foundry.creatures import AllTemplates
from foe_foundry.utils import name_to_key
from foe_foundry_data.families import load_families
from foe_foundry_data.powers import Powers
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

    # Add POW nodes
    for power in Powers.AllPowers:
        node_id = f"POW:{power.key}"
        G.add_node(
            node_id,
            type="POW",
            power_key=power.key,
        )

        for monster in power.monsters:
            monster_node_id = f"FF_MON:{monster.key}"
            if G.has_node(monster_node_id):
                G.add_edge(node_id, monster_node_id, type="grants")
            else:
                issues.append(
                    f"POW {power.key} references unknown FF_MON {monster.key}"
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
        pos = nx.spring_layout(subgraph, seed=42, k=None)

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
                return (
                    priority["MON_SRD"]
                    if node.get("is_srd", False)
                    else priority["MON"]
                )
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
                node_sizes[n] = 50
                # No label for DOC nodes
            elif node_type == "FF_MON":
                node_colors[n] = "#8B0000"  # dark red
                node_sizes[n] = 300
                # Label is just the key, e.g. 'wolf' for 'FF_MON:wolf'
                labels[n] = n.split(":", 1)[-1]
            elif node_type == "FF_FAM":
                node_colors[n] = "#FFB6B6"  # light red
                node_sizes[n] = 400
                labels[n] = subgraph.nodes[n].get("family_key", n)
            elif node_type == "POW":
                node_colors[n] = "#800080"  # purple
                node_sizes[n] = 50  # Match DOC node size
                # No label for POW nodes
            elif node_type == "MON":
                is_srd = subgraph.nodes[n].get("is_srd", False)
                node_colors[n] = "#2ca02c" if is_srd else "#ff7f0e"
                node_sizes[n] = 300 if is_srd else 150
                labels[n] = subgraph.nodes[n].get("name", n)
                mon_labels[n] = labels[n]
            else:
                node_colors[n] = "#cccccc"
                node_sizes[n] = 100

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
                    alpha=0.9,
                    label="MON",
                )
                nx.draw_networkx_nodes(
                    subgraph,
                    pos,
                    nodelist=srd_nodes,
                    node_color=[node_colors[n] for n in srd_nodes],
                    node_size=[node_sizes[n] for n in srd_nodes],
                    alpha=1.0,
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
                    alpha=1.0,
                    label=t,
                )

        # Draw edges
        nx.draw_networkx_edges(subgraph, pos, alpha=0.3)

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

        plt.title("Sampled Foe Foundry GraphRAG")
        plt.tight_layout()
        out_path = os.path.join(
            os.path.dirname(__file__), "foe_foundry_graph_sampled.png"
        )
        plt.savefig(out_path, dpi=300)
        print(f"Sampled graph visualization saved to {out_path}")
    except ImportError:
        print("matplotlib not installed; skipping visualization.")


if __name__ == "__main__":
    dotenv.load_dotenv()
    main()

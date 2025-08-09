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

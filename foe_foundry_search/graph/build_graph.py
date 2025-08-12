"""
Graph Construction for Foe Foundry Search
=========================================

This module builds a directed graph using NetworkX to represent relationships between monsters, documents, families, and powers in the Foe Foundry system.

Nodes:
    - DOC: Monster documents
    - MON: Monster metadata
    - FF_MON: Foe Foundry monster instances
    - FF_FAM: Monster families
    - POW: Powers

Edges:
    - DOC → MON: Document describes monster
    - MON → MON: Similar monsters (SRD mapping)
    - FF_MON → MON: FF monster implements SRD monster
    - FF_MON → MON: FF monster implements other monster
    - FF_FAM → FF_MON: Family membership
    - POW → FF_MON: Power grants to monster

Returns a tuple of (graph, issues) where issues is a list of warnings or missing references.
"""

import json
import os
from functools import cached_property
from pathlib import Path

import networkx as nx

from foe_foundry.creatures import AllTemplates
from foe_foundry.utils import name_to_key
from foe_foundry_data.families import load_families
from foe_foundry_data.monsters.all import Monsters
from foe_foundry_data.powers import Powers
from foe_foundry_search.documents import (
    DocType,
    iter_documents,
    load_monster_document_metas,
)
from foe_foundry_search.documents.meta import MonsterDocumentMeta

# Path to SRD mapping file
SRD_MAPPING_PATH = Path(__file__).parent / "monster_to_srd_a_b.json"
CACHE_DIR = Path.cwd() / "cache" / "graph"
CACHE_FILE = CACHE_DIR / "graph.json"


class _Cache:
    def __init__(self):
        self.issues = []

    @cached_property
    def load_graph(self) -> nx.DiGraph:
        """Load the graph from the cache or build it if not cached."""

        CACHE_DIR.mkdir(exist_ok=True, parents=True)

        if CACHE_FILE.exists():
            # Load from cache
            with open(CACHE_FILE, "r") as f:
                data = json.load(f)
            return nx.node_link_graph(data)
        else:
            # Build and cache
            graph, issues = _do_build_graph()

            # Save to cache
            data = nx.node_link_data(graph, edges="links")
            with open(CACHE_FILE, "w") as f:
                json.dump(data, f, indent=2)

            with open(CACHE_DIR / "issues.txt", "w") as f:
                f.writelines(f"{issue}\n" for issue in self.issues)

            self.issues = issues
            return graph


_cache = _Cache()


def load_graph() -> nx.DiGraph:
    """Load the graph from the cache or build it if not cached."""
    return _cache.load_graph


def rebuild_graph() -> nx.DiGraph:
    """Rebuild the graph from scratch."""

    # delete file-system cache
    if CACHE_FILE.exists():
        CACHE_FILE.unlink()

    # hack to clear the @cached_property cache
    if "load_graph" in _cache.__dict__:
        del _cache.__dict__["load_graph"]

    return _cache.load_graph


def _do_build_graph() -> tuple[nx.DiGraph, list[str]]:
    """
    Build a directed graph representing monsters, documents, families, and powers.

    Returns:
        tuple[nx.DiGraph, list[str]]: The constructed graph and a list of issues encountered (missing references, etc).
    """
    G = nx.DiGraph()

    issues = []

    # Add DOC nodes
    for doc in iter_documents():
        node_id = f"DOC:{doc.doc_id}"
        G.add_node(
            node_id,
            type="DOC",
            name=doc.name,
            doc_type=doc.doc_type,
            monster_key=doc.monster_key,
            power_key=doc.power_key,
        )

    # Add MON nodes: Each represents monster metadata
    metas: dict[str, MonsterDocumentMeta] = load_monster_document_metas()
    for key, meta in metas.items():
        node_id = f"MON:{key}"
        G.add_node(
            node_id,
            type="MON",
            name=meta.name,
            monster_key=doc.monster_key,
            is_srd=meta.srd,
        )

    # Add POW nodes: Powers and the monsters they grant to
    for power in Powers.AllPowers:
        node_id = f"POW:{power.key}"
        G.add_node(
            node_id,
            type="POW",
            power_key=power.key,
        )

    # Add FF_MON nodes: Foe Foundry monster instances and their SRD/other references
    for monster in Monsters.one_of_each_monster:
        node_id = f"FF_MON:{monster.key}"
        G.add_node(
            node_id,
            type="FF_MON",
            monster_key=monster.key,
            template_key=monster.template_key,
            cr=monster.cr,
            creature_type=monster.creature_type,
        )

    # Add FF_FAM nodes: Monster families and their members
    for family in load_families():
        node_id = f"FF_FAM:{family.key}"
        G.add_node(
            node_id,
            type="FF_FAM",
            family_key=family.key,
        )

    # Add DOC → MON edges: Document describes monster
    for doc in iter_documents():
        if doc.monster_key is None:
            continue

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

    # Add DOC → MON edges: Document is a blog post that references a monster
    with (Path.cwd() / "data" / "the_monsters_know" / "references.json").open("r") as f:
        blog_references = json.load(f)

    for doc in iter_documents():
        if doc.doc_type != DocType.blog_post:
            continue

        key = doc.doc_id[5:] + ".md"  # remove the thmk- prefix
        references = blog_references.get(key, [])

        for reference in references:
            monster_key = name_to_key(reference)
            monster_node = f"MON:{monster_key}"
            doc_node = f"DOC:{doc.doc_id}"

            if not G.has_node(monster_node):
                issues.append(
                    f"Blog post {doc.doc_id} references unknown monster {monster_key}"
                )
                continue

            G.add_edge(
                doc_node,
                monster_node,
                type="references",
                relevancy=1.0,
            )

    # Add DOC → POW edges: Document describes power
    for doc in iter_documents():
        if doc.power_key is None:
            continue

        G.add_edge(
            f"DOC:{doc.doc_id}", f"POW:{doc.power_key}", type="about", relevance=1.0
        )

    # Add MON → MON edges: Similar monsters via SRD mapping
    for monster_key, meta in metas.items():
        for similar_key, similar_type in meta.similar_monsters.items():
            # skip self references, we know SRD monsters reference themselves
            if monster_key == similar_key:
                continue

            if not G.has_node(f"MON:{similar_key}"):
                issues.append(
                    f"MON {monster_key} references unknown similar monster {similar_key}"
                )
                continue

            G.add_edge(
                f"MON:{monster_key}",
                f"MON:{similar_key}",
                type="similar",
                similar_type=similar_type.value,
                relevancy=similar_type.relevancy,
            )
    if os.path.exists(SRD_MAPPING_PATH):
        with open(SRD_MAPPING_PATH, "r") as f:
            srd_map = json.load(f)
        for monster_name, srd_names in srd_map.items():
            if srd_names is None:
                continue

            monster_key = name_to_key(monster_name)

            for srd_name in srd_names:
                srd_monster_key = name_to_key(srd_name)

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

    # Add POW → FF_MON edges
    for power in Powers.AllPowers:
        for monster in power.monsters:
            power_node_id = f"POW:{power.key}"
            monster_node_id = f"FF_MON:{monster.key}"
            if G.has_node(monster_node_id):
                G.add_edge(power_node_id, monster_node_id, type="has_power")
            else:
                issues.append(
                    f"POW {power.key} references unknown FF_MON {monster.key}"
                )

    # Add MON → FF_MON edges: alias of third party monsters to Foe Foundry monsters
    for template in AllTemplates:
        for variant in template.variants:
            for monster in variant.monsters:
                ff_node_id = f"FF_MON:{monster.key}"

                # SRD References
                for srd_creature in monster.srd_creatures or []:
                    srd_monster_key = name_to_key(srd_creature)
                    srd_node_id = f"MON:{srd_monster_key}"

                    if G.has_node(srd_node_id):
                        G.add_edge(srd_node_id, ff_node_id, type="alias")
                    else:
                        issues.append(
                            f"FF_MON {monster.key} references unknown monster {srd_creature}"
                        )

                # Other References
                for other_monster_name, _ in (monster.other_creatures or {}).items():
                    other_monster_key = name_to_key(other_monster_name)
                    other_node_id = f"MON:{other_monster_key}"

                    if G.has_node(other_node_id):
                        G.add_edge(ff_node_id, other_node_id, type="alias")
                    else:
                        issues.append(
                            f"FF_MON {monster.key} references unknown other creature {other_monster_name}"
                        )

    # Add FF_MON → FF_FAM edges: monsters are assigned to familes
    for family in load_families():
        family_node_id = f"FF_FAM:{family.key}"
        for monster in family.monsters:
            monster_node_id = f"FF_MON:{monster.key}"
            if G.has_node(monster_node_id):
                G.add_edge(monster_node_id, family_node_id, type="member")
            else:
                issues.append(
                    f"FF_FAM {family.key} references unknown FF_MON {monster.key}"
                )

    return G, issues

import re
from pathlib import Path

import numpy as np
from langchain_core.tools import tool

from foe_foundry_data.monsters import Monsters
from foe_foundry_search.documents import load_monster_document_metas
from foe_foundry_search.search import (
    DocumentSearchResult,
    EntityType,
    search_entities_with_graph_expansion,
)


@tool
def search_monsters(keywords: str) -> str:
    """
    Search for monsters using natural language keywords and return a formatted Markdown list of matching monsters.

    This tool leverages semantic and graph-based search to find monsters from both canonical and third-party sources.
    Results include monster name, description, challenge rating (CR), type, and relevant document matches.
    Suitable for LLMs and chatbots to provide rich, linkable search results for tabletop RPG monster queries.

    Args:
        keywords (str): Natural language keywords describing the desired monsters.

    Returns:
        str: Markdown-formatted search results, or an error message if the search fails.
    """

    try:
        monster_metas = load_monster_document_metas()

        results = search_entities_with_graph_expansion(
            keywords, entity_types={EntityType.MONSTER, EntityType.MONSTER_THIRD_PARTY}
        )

        messages = []
        monster_keys = set()
        for result in results:
            if result.monster_key is None or result.monster_key in monster_keys:
                continue

            if result.entity_type == EntityType.MONSTER:
                monster_key = result.monster_key
                monster = Monsters.lookup[monster_key]
                url = f"https://foefoundry.com/monsters/{monster.template_key}/#{monster.key}"
                message = f"- [{monster.name}]({url}) (CR: {monster.cr}, Type: {monster.creature_type}). {monster.tag_line}.\n"
                message += _document_matches_to_message(result.document_matches)
                message += "\n\n"
                monster_keys.add(monster_key)
                messages.append(message)
            else:
                monster_key = result.monster_key
                monster = monster_metas.get(monster_key)
                if monster is None:
                    continue

                url = f"monster://{monster.key}"
                message = f"- [{monster.name}]({url}) (CR: {monster.cr}, Type: {monster.creature_type}). {monster.description}.\n"
                message += _document_matches_to_message(result.document_matches)
                message += "\n\n"
                monster_keys.add(monster_key)
                messages.append(message)

        return f"\n## Monster Search Results For: {keywords}\n\n" + "\n".join(messages)

    except Exception as x:
        return f"Error occurred while searching for monsters: {x}"


@tool
def get_monster_detail(url_or_key: str) -> str:
    """
    Retrieve detailed statblock or description for a monster given its URL or key.

    This tool resolves Foe Foundry URLs, internal monster URLs, or plain monster keys, and returns either HTML or Markdown
    containing the monster's statblock or descriptive paragraphs. Useful for LLMs needing to answer questions about specific monsters.

    Args:
        url_or_key (str): Foe Foundry monster URL, internal monster URL, or monster key.

    Returns:
        str: HTML or Markdown with the monster's statblock or description, or an error message if not found.
    """

    try:
        rng = np.random.default_rng()

        monster_metas = load_monster_document_metas()

        monster_key = _resolve_url_or_key(url_or_key)

        monster_ff = Monsters.lookup.get(monster_key)
        monster_meta = monster_metas.get(monster_key)

        if monster_ff is not None:
            return (
                f"\n# {monster_ff.name}\n\n"
                + (monster_ff.overview_html or "")
                + "\n"
                + monster_ff.statblock_html
            )
        if monster_meta is not None:
            monster_meta.key

            # If we can find the raw markdown file containing the monster, then retrieve it
            # That's because it contains the actual statblock
            # Otherwise, use the metadata paragraphs

            path = Path.cwd() / "data" / "5e_canonical" / f"{monster_meta.key}.md"
            if path.exists():
                with open(path, "r") as f:
                    return f.read()
            else:
                content = f"\n# {monster_meta.name}\n\n"
                for _, paragraph in monster_meta.iter_paragraphs(rng):
                    content += f"{paragraph}\n"
                return content

        else:
            return f"No monster found for URL or key: {url_or_key}."
    except Exception as x:
        return f"Error occurred while retrieving monster details: {x}"


def _resolve_url_or_key(url_or_key: str) -> str:
    ff_pattern = r"^https://foefoundry\.com/monsters/[^/]+/#.+$"
    internal_pattern = r"^monster://.+$"

    if re.match(ff_pattern, url_or_key):
        # Handle Foe Foundry monster URL
        # Example: https://foefoundry.com/monsters/{template_key}/#{monster_key}
        match = re.search(
            r"^https://foefoundry\.com/monsters/[^/]+/#(?P<monster_key>.+)$", url_or_key
        )
        monster_key = match.group("monster_key")  # type: ignore
        return str(monster_key)
    elif re.match(internal_pattern, url_or_key):
        # Handle internal monster key URL
        # Example: monster://{monster_key}
        match = re.search(r"^monster://(?P<monster_key>.+)$", url_or_key)
        monster_key = match.group("monster_key")  # type: ignore
        return str(monster_key)
    else:
        # Handle as a plain monster key or invalid input
        return url_or_key


def _document_matches_to_message(docs: list[DocumentSearchResult]) -> str:
    messages = []
    for doc in docs:
        highlight = f"({doc.highlighted_match})" if doc.highlighted_match else ""
        messages.append(
            f"  - [{doc.document.name}]({doc.document.doc_id}): {highlight}"
        )
    return "\n".join(messages)

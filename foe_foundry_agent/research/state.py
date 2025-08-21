from typing import Literal, TypedDict

from langchain_core.messages import ToolCall
from pydantic import BaseModel

from foe_foundry.utils.md import extract_md_blocks_from_text
from foe_foundry.utils.monster_content import (
    extract_yaml_frontmatter,
    strip_yaml_frontmatter,
)

from ..messages import InMemoryHistory


class ResearchNote(BaseModel):
    type: Literal["relevant-monster", "scratchpad"]
    relevance: Literal["high", "medium", "low"]
    monster_key: str | None
    research_summary: str
    source_refs: str
    research_content: str


def parse_research_notes(llm_output: str) -> list[ResearchNote]:
    notes = []
    md_blocks = extract_md_blocks_from_text(llm_output)
    for block in md_blocks:
        yaml_data = extract_yaml_frontmatter(block)
        content = strip_yaml_frontmatter(block).strip()
        note = ResearchNote(
            type=yaml_data.get("type", "scratchpad"),
            relevance=yaml_data.get("relevance", "medium"),
            monster_key=yaml_data.get("monster_key"),
            research_summary=yaml_data.get("research_summary", ""),
            source_refs=yaml_data.get("source_refs", ""),
            research_content=content,
        )
        notes.append(note)
    return notes


class ResearchState(TypedDict):
    messages: InMemoryHistory
    notes: list[ResearchNote] | None
    tool_calls: list[ToolCall] | None
    search_tool_count: int
    detail_tool_count: int

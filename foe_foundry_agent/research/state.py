from typing import Literal, TypedDict

import yaml
from langchain_core.messages import ToolCall
from pydantic import BaseModel

from foe_foundry.utils.md import extract_md_blocks_from_text
from foe_foundry.utils.monster_content import (
    extract_yaml_frontmatter,
    strip_yaml_frontmatter,
)

from ..messages import InMemoryHistory


class ResearchNote(BaseModel):
    type: Literal["relevant-monster", "relevant-power", "scratchpad"]
    relevance: Literal["high", "medium", "low"]
    monster_key: str | None
    power_key: str | None
    source_refs: str | None
    research_summary: str
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
            power_key=yaml_data.get("power_key"),
            research_summary=yaml_data.get("research_summary", ""),
            source_refs=yaml_data.get("source_refs"),
            research_content=content,
        )
        notes.append(note)
    return notes


class ResearchState(TypedDict):
    messages: InMemoryHistory
    notes: list[ResearchNote] | None
    tool_calls: list[ToolCall] | None
    overall_summary: str | None
    force_exit: bool

    budget_search_monsters: int
    budget_search_powers: int
    budget_monster_details: int


class ResearchResult(BaseModel):
    messages: InMemoryHistory
    notes: list[ResearchNote]
    overall_summary: str

    def to_llm_display_text(self):
        return (
            "```yaml\n"
            + yaml.safe_dump(self.model_dump(mode="json"), sort_keys=False)
            + "```"
        )

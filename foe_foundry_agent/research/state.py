from pydantic import BaseModel


class MonsterResearch(BaseModel):
    monster_key: str
    monster_name: str
    research_notes: str
    statblock_md: str | None


class Scratchpad(BaseModel):
    content: str


class ResearchState(BaseModel):
    scratchpads: list[Scratchpad]
    monsters: list[MonsterResearch]
    turns: int
    complete: bool

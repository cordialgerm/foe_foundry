from __future__ import annotations

from enum import StrEnum

import yaml
from pydantic import BaseModel

from foe_foundry.utils.yaml import extract_yaml_block_from_text


class MonsterRecognizedAs(StrEnum):
    srd = "srd"
    srd_variant = "srd_variant"
    fantasy_ttrpg = "fantasy_ttrpg"
    fantasy_general = "fantasy_general"
    unknown = "unknown"


class PlanState(BaseModel):
    monster_recognized_as: MonsterRecognizedAs
    monster_name: str | None
    monster_fantasy: str | None
    monster_appearance: str | None
    monster_behavior: str | None
    monster_abilities: str | None
    monster_environment: str | None
    inferred_fields: list[str] | None
    missing_information_query: str | None

    @staticmethod
    def from_llm_output(output: str) -> PlanState:
        """Parses a PlanState from the output of an LLM call, which may contain slightly noisy YAML."""
        data: dict = extract_yaml_block_from_text(output)

        data["monster_recognized_as"] = MonsterRecognizedAs(
            data["monster_recognized_as"]
        )

        return PlanState(**data)

    def to_llm_display_text(self, fence: bool = True) -> str:
        yaml_text = yaml.safe_dump(self.model_dump(mode="json"), sort_keys=False)
        if fence:
            return f"```yaml\n{yaml_text}```"
        return yaml_text

    @property
    def is_complete(self) -> bool:
        return self.missing_information_query is None

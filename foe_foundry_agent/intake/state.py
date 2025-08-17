from __future__ import annotations

import yaml
from pydantic import BaseModel

from foe_foundry.utils.md import extract_md_block_from_text
from foe_foundry.utils.yaml import extract_yaml_block_from_text


class IntakeState(BaseModel):
    statblock_markdown: str | None
    additional_notes: str | None
    is_statblock_complete: bool = False
    is_relevant: bool = False
    clarification_follow_up: str | None = None

    def to_llm_display_text(self) -> str:
        yaml_text = yaml.safe_dump(self.model_dump(mode="json"), sort_keys=False)
        return (
            f"```yaml\n{yaml_text}\n```\n\n```md\n{self.statblock_markdown or ''}\n```"
        )

    @staticmethod
    def from_llm_output(output: str) -> IntakeState:
        args = extract_yaml_block_from_text(output)
        md = extract_md_block_from_text(output)

        clarification = args.get("clarification_follow_up")
        if md is None and clarification is None:
            clarification = "It doesn't seem like a monster statblock was included. Can you please provide one?"

        return IntakeState(
            statblock_markdown=md,
            additional_notes=args.get("additional_notes", None),
            is_statblock_complete=args.get("is_statblock_complete", False)
            and md is not None,
            is_relevant=args.get("is_relevant", False),
            clarification_follow_up=clarification,
        )

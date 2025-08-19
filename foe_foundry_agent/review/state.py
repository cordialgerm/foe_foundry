from __future__ import annotations

from pydantic import BaseModel

from foe_foundry.utils.yaml import extract_yaml_block_from_text


class ReviewState(BaseModel):
    review_request: str
    requested_node: str
    feedback_summary: str | None
    is_approved: bool | None

    @staticmethod
    def from_llm_output(output: str) -> ReviewState:
        args = extract_yaml_block_from_text(output)
        return ReviewState(**args)

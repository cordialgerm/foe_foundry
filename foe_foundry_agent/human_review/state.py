from __future__ import annotations

from pydantic import BaseModel

from foe_foundry.utils.yaml import extract_yaml_block_from_text


class HumanReviewState(BaseModel):
    review_requested: str
    return_node: str
    next_node: str
    review_provided: str | None = None
    is_approved: bool | None = None

    def with_human_response(self, response: str) -> HumanReviewState:
        return self.model_copy(update=dict(review_provided=response))

    def with_llm_response(self, output: str) -> HumanReviewState:
        args = extract_yaml_block_from_text(output)
        return self.model_copy(update=dict(is_approved=args.get("is_approved", False)))

    @property
    def next_edge(self) -> str:
        if self.is_approved is None:
            return "human_review"
        elif self.is_approved:
            return self.next_node
        else:
            return self.return_node

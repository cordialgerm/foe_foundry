from __future__ import annotations

from pydantic import BaseModel


class HumanInputState(BaseModel):
    input_requested: str
    return_node: str
    input_provided: str | None = None

    def with_response(self, response: str) -> HumanInputState:
        return self.model_copy(update=dict(input_provided=response))

    @property
    def next_edge(self) -> str:
        return self.return_node if self.input_provided is not None else "human_input"

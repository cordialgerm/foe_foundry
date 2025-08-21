from typing import Union
from uuid import uuid4

from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    ToolCall,
    ToolMessage,
    get_buffer_string,
    messages_from_dict,
    messages_to_dict,
)
from pydantic import BaseModel, Field


class InMemoryHistory(BaseModel):
    """LangGraph-compatible chat history using safe message serialization."""

    message_dicts: list[dict] = Field(default_factory=list)

    @property
    def messages(self) -> list[BaseMessage]:
        return messages_from_dict(self.message_dicts)

    def add_messages(self, new_messages: list[BaseMessage]):
        self.message_dicts.extend(messages_to_dict(new_messages))

    def clear(self) -> None:
        self.message_dicts.clear()

    def add_user_message(self, message: HumanMessage | str):
        """Convenience method for adding a human message string to the store.

        Please note that this is a convenience method. Code should favor the
        bulk add_messages interface instead to save on round-trips to the underlying
        persistence layer.

        This method may be deprecated in a future release.

        Args:
            message: The human message to add to the store.
        """
        if isinstance(message, HumanMessage):
            self.add_message(message)
        else:
            self.add_message(HumanMessage(content=message, id=str(uuid4())))

    def add_ai_message(self, message: Union[AIMessage, str]):
        """Convenience method for adding an AI message string to the store.

        Please note that this is a convenience method. Code should favor the bulk
        add_messages interface instead to save on round-trips to the underlying
        persistence layer.

        This method may be deprecated in a future release.

        Args:
            message: The AI message to add.
        """
        if isinstance(message, AIMessage):
            self.add_message(message)
        else:
            self.add_message(AIMessage(content=message, id=str(uuid4())))

    def add_tool_call(self, tool_call: ToolCall):
        """Add a ToolCall object to the store."""

        self.message_dicts.append(
            {
                "type": "ai",
                "data": {"content": "Calling tool..", "tool_calls": [tool_call]},
            }
        )

    def add_tool_message(self, tool_message: ToolMessage):
        """Add a ToolMessage object to the store."""
        self.add_message(tool_message)

    def add_message(self, message: BaseMessage):
        """Add a Message object to the store.

        Args:
            message: A BaseMessage object to store.

        Raises:
            NotImplementedError: If the sub-class has not implemented an efficient
                add_messages method.
        """
        self.add_messages([message])

    def __str__(self) -> str:
        """Return a string representation of the chat history."""
        return get_buffer_string(self.messages)

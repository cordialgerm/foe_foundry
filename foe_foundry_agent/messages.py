from typing import Union
from uuid import uuid4

from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    SystemMessage,
    ToolCall,
    ToolMessage,
    get_buffer_string,
    messages_from_dict,
    messages_to_dict,
)
from pydantic import BaseModel, Field


class InMemoryHistory(BaseModel):
    """
    In-memory chat history compatible with LangGraph, using safe message serialization.
    Stores messages as dictionaries for persistence and interoperability.
    Provides convenience methods for adding different message types and managing history.
    """

    message_dicts: list[dict] = Field(default_factory=list)

    def __init__(self, **data):
        super().__init__(**data)
        self._on_message_added = []

    def add_message_listener(self, callback):
        """
        Register a callback to be called when a message is added.
        Callback signature: def callback(message: BaseMessage, history: InMemoryHistory)
        """
        self._on_message_added.append(callback)

    def remove_message_listener(self, callback):
        """
        Unregister a previously registered callback.
        """
        self._on_message_added.remove(callback)

    def _trigger_message_added(self, message: BaseMessage):
        for cb in self._on_message_added:
            cb(message, self)

    @property
    def messages(self) -> list[BaseMessage]:
        """
        Returns the list of chat messages as BaseMessage objects, deserialized from stored dictionaries.
        """
        return messages_from_dict(self.message_dicts)

    def add_messages(self, new_messages: list[BaseMessage]):
        """
        Add multiple BaseMessage objects to the chat history.

        Args:
            new_messages: List of BaseMessage objects to add.
        """
        self.message_dicts.extend(messages_to_dict(new_messages))
        for msg in new_messages:
            self._trigger_message_added(msg)

    def clear(self) -> None:
        """
        Remove all messages from the chat history.
        """
        self.message_dicts.clear()

    def add_user_message(self, message: HumanMessage | str):
        """
        Add a human (user) message to the chat history.

        Args:
            message: The human message to add, either as a HumanMessage object or a string.

        Note:
            Prefer using add_messages for bulk operations to optimize performance.
        """
        if isinstance(message, HumanMessage):
            self.add_message(message)
        else:
            self.add_message(HumanMessage(content=message, id=str(uuid4())))

    def add_ai_message(self, message: Union[AIMessage, str]):
        """
        Add an AI message to the chat history.

        Args:
            message: The AI message to add, either as an AIMessage object or a string.

        Note:
            Prefer using add_messages for bulk operations to optimize performance.
        """
        if isinstance(message, AIMessage):
            self.add_message(message)
        else:
            self.add_message(AIMessage(content=message, id=str(uuid4())))

    def add_system_message(self, message: Union[SystemMessage, str]):
        """
        Add a system message to the chat history.

        Args:
            message: The system message to add, either as a SystemMessage object or a string.
        """
        if isinstance(message, SystemMessage):
            self.add_message(message)
        else:
            self.add_message(SystemMessage(content=message, id=str(uuid4())))

    def add_tool_call(self, tool_call: ToolCall):
        """
        Add a ToolCall object to the chat history as an AI message indicating a tool is being called.

        Args:
            tool_call: The ToolCall object to add.
        """
        msg_dict = {
            "type": "ai",
            "data": {"content": "Calling tool..", "tool_calls": [tool_call]},
        }
        msg = messages_from_dict([msg_dict])[0]
        self.add_message(msg)

    def add_tool_message(self, tool_message: ToolMessage):
        """
        Add a ToolMessage object to the chat history.

        Args:
            tool_message: The ToolMessage object to add.
        """
        self.add_message(tool_message)

    def add_message(self, message: BaseMessage):
        """
        Add a single BaseMessage object to the chat history.

        Args:
            message: A BaseMessage object to store.
        """
        self.add_messages([message])

    def __str__(self) -> str:
        """
        Return a formatted string representation of the chat history for display or logging.
        """
        return get_buffer_string(self.messages)

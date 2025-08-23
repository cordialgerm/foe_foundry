from typing import TYPE_CHECKING

from langchain_core.messages import BaseMessage

from .types import MessageCallback

if TYPE_CHECKING:
    from .messages import InMemoryHistory


class _EventDispatcher:
    """
    Internal event dispatcher for message events.
    Allows listeners to be registered and emits events to them.
    """

    def __init__(self):
        """Initialize the dispatcher with an empty listener list."""
        self.listeners = []

    def add_listener(self, callback: MessageCallback):
        """
        Add a listener callback to the dispatcher.
        Args:
            callback (MessageCallback): The callback to register.
        """
        self.listeners.append(callback)

    def emit(self, *args, **kwargs):
        """
        Emit an event to all registered listeners.
        Args:
            *args: Positional arguments for the callback.
            **kwargs: Keyword arguments for the callback.
        """
        for listener in self.listeners:
            listener(*args, **kwargs)


dispatcher = _EventDispatcher()


def add_message_listener(callback: MessageCallback):
    """
    Register a callback to be notified when a message event occurs.
    Args:
        callback (MessageCallback): The callback to register.
    """
    dispatcher.add_listener(callback)


def emit_message_event(message: BaseMessage, history: "InMemoryHistory"):
    """
    Emit a message event to all registered listeners.
    Args:
        message (BaseMessage): The message to emit.
        history (InMemoryHistory): The message history.
    """
    dispatcher.emit(message, history)

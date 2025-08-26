from typing import TYPE_CHECKING

from langchain_core.messages import BaseMessage

from .types import MessageCallback, StateCallback

if TYPE_CHECKING:
    from ..messages.messages import InMemoryHistory
    from ..state import StateChangedEvent


class _EventDispatcher:
    """
    Internal event dispatcher for message events.
    Allows listeners to be registered and emits events to them.
    """

    def __init__(self):
        """Initialize the dispatcher with an empty listener list."""
        self.message_listeners = []
        self.state_listeners = []

    def add_message_listener(self, callback: MessageCallback):
        """
        Add a listener callback to the dispatcher.
        Args:
            callback (MessageCallback): The callback to register.
        """
        self.message_listeners.append(callback)

    def emit_message(self, *args, **kwargs):
        """
        Emit an event to all registered listeners.
        Args:
            *args: Positional arguments for the callback.
            **kwargs: Keyword arguments for the callback.
        """
        for listener in self.message_listeners:
            listener(*args, **kwargs)

    def add_state_listener(self, callback: StateCallback):
        """
        Add a state change listener callback to the dispatcher.
        Args:
            callback (StateCallback): The callback to register.
        """
        self.state_listeners.append(callback)

    def emit_state(self, *args, **kwargs):
        """
        Emit a state change event to all registered listeners.
        Args:
            event (StateChangedEvent): The state change event to emit.
        """
        for listener in self.state_listeners:
            listener(*args, **kwargs)


dispatcher = _EventDispatcher()


def add_message_listener(callback: MessageCallback):
    """
    Register a callback to be notified when a message event occurs.
    Args:
        callback (MessageCallback): The callback to register.
    """
    dispatcher.add_message_listener(callback)


def emit_message_event(message: BaseMessage, history: "InMemoryHistory"):
    """
    Emit a message event to all registered listeners.
    Args:
        message (BaseMessage): The message to emit.
        history (InMemoryHistory): The message history.
    """
    dispatcher.emit_message(message, history)


def add_state_listener(callback: StateCallback):
    """
    Register a callback to be notified when a state change event occurs.
    Args:
        callback (StateCallback): The callback to register.
    """
    dispatcher.add_state_listener(callback)


def emit_state_event(event: "StateChangedEvent"):
    """
    Emit a state change event to all registered listeners.
    Args:
        event (StateChangedEvent): The state change event to emit.
    """
    dispatcher.emit_state(event)

from langchain_core.messages import BaseMessage  # noqa


from typing import Callable, TypeAlias, TYPE_CHECKING


if TYPE_CHECKING:
    from ..messages.messages import InMemoryHistory
    from ..state import StateChangedEvent


MessageCallback: TypeAlias = Callable[[BaseMessage, "InMemoryHistory"], None]
StateCallback: TypeAlias = Callable[["StateChangedEvent"], None]

from langchain_core.messages import BaseMessage  # noqa

from typing import Callable, TypeAlias
from .messages import InMemoryHistory  # noqa


MessageCallback: TypeAlias = Callable[[BaseMessage, "InMemoryHistory"], None]

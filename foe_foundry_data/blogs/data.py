from dataclasses import dataclass
from datetime import datetime


@dataclass(kw_only=True, frozen=True)
class BlogPost:
    title: str
    description: str
    url: str
    image: str
    date: datetime
    image_has_transparent_edges: bool

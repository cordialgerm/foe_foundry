from dataclasses import dataclass, field

from markdown import Markdown

from ..refs import MonsterRef, Power
from .ext import FoeFoundryMdExtension


@dataclass(kw_only=True)
class RenderedMarkdown:
    html: str
    toc: str | None
    header: str
    references: list[MonsterRef | Power] = field(default_factory=list)


def markdown(text: str, strip_header: bool = True) -> RenderedMarkdown:
    """Renders a markdown string into HTML and returns the header, toc, and html"""

    # if text starts with an h1 header, remove that line
    if text.startswith("# "):
        lines = text.splitlines(keepends=True)
        header_line = lines[0]
        header = header_line[1:].strip()
        if strip_header:
            lines = lines[1:]
        text = "".join(lines)
    else:
        header = ""

    ext = FoeFoundryMdExtension()
    md = Markdown(
        extensions=["toc", "tables", "attr_list", "md_in_html", "admonition", ext],
        extension_configs={
            "toc": {
                "permalink": True  # adds a link symbol next to headers
            }
        },
    )
    html = md.convert(text)
    toc = md.toc  # type: ignore

    return RenderedMarkdown(
        html=html, toc=toc, header=header, references=ext.resolved_references
    )

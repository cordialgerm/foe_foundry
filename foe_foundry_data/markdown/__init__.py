from .md import RenderedMarkdown, markdown  # noqa
from .monster_link import monster_link, monster_button  # noqa
from .ext import FoeFoundryMdExtension  # noqa


def makeExtension(**kwargs):
    return FoeFoundryMdExtension(**kwargs)

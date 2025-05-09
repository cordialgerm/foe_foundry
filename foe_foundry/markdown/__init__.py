from .md import RenderedMarkdown, markdown  # noqa
from .monster_ref import MonsterRef, MonsterRefResolver  # noqa
from .monster_link import monster_link, monster_button  # noqa
from .ext import MonsterLinkExtension  # noqa


def makeExtension(**kwargs):
    return MonsterLinkExtension(**kwargs)

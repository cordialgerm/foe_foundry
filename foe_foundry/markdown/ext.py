import os
import re

from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor

from .monster_link import monster_button, monster_link, monster_statblock
from .monster_ref import MonsterRefResolver


class MonsterLinkExtension(Extension):
    def __init__(self, **kwargs):
        self.config = {}
        self.ref_resolver = MonsterRefResolver()
        self.resolved_refences = []

        base_url = kwargs.get("base_url", os.environ.get("SITE_URL"))
        if base_url is None:
            raise ValueError(
                "base_url must be provided or set in the environment as SITE_URL"
            )
        self.base_url = base_url

        super().__init__(**kwargs)

    def extendMarkdown(self, md):
        md.preprocessors.register(
            MonsterLinkPreprocessor(
                md, self.base_url, self.ref_resolver, self.resolved_refences
            ),
            "monster_link",
            175,
        )


class MonsterLinkPreprocessor(Preprocessor):
    MONSTER_LINK_RE = re.compile(r"\[\[(?P<name1>.+?)\]\]|\*\*(?P<name2>.+?)\*\*")
    MONSTER_BUTTON_RE = re.compile(r"\[\[\$(?P<name3>.+?)\]\]")
    MONSTER_STATBLOCK_RE = re.compile(r"\[\[!(?P<name4>.+?)\]\]")

    def __init__(
        self,
        md,
        base_url: str,
        ref_resolver: MonsterRefResolver,
        resolved_refences: list,
    ):
        super().__init__(md)
        self.base_url = base_url
        self.ref_resolver = ref_resolver
        self.resolved_references = resolved_refences

    def run(self, lines):
        new_lines = []
        for line in lines:
            new_line = self.MONSTER_STATBLOCK_RE.sub(self.replace_statblock, line)
            new_line = self.MONSTER_BUTTON_RE.sub(self.replace_button, new_line)
            new_line = self.MONSTER_LINK_RE.sub(self.replace_link, new_line)
            new_lines.append(new_line)
        return new_lines

    def replace_link(self, match: re.Match):
        if match.group("name1"):
            monster_name = match.group("name1")
        elif match.group("name2"):
            monster_name = match.group("name2")
        else:
            raise ValueError("No monster name found in match")

        ref = self.ref_resolver.resolve_monster_ref(monster_name)
        if ref is None:
            return f"<b>{monster_name}</b>"

        self.resolved_references.append(ref)
        return str(monster_link(ref, self.base_url))

    def replace_button(self, match: re.Match):
        if match.group("name3"):
            monster_name = match.group("name3")
        else:
            raise ValueError("No monster name found in match")

        ref = self.ref_resolver.resolve_monster_ref(monster_name)
        if ref is not None:
            self.resolved_references.append(ref)
            return str(monster_button(ref, self.base_url))
        else:
            return match.group(0)  # Return the original text if no match is found

    def replace_statblock(self, match: re.Match):
        if match.group("name4"):
            monster_name = match.group("name4")
        else:
            raise ValueError("No monster name found in match")

        ref = self.ref_resolver.resolve_monster_ref(monster_name)
        if ref is not None:
            self.resolved_references.append(ref)
            return str(monster_statblock(ref))
        else:
            return match.group(0)

import os
import re

from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor

from ..jinja import render_power_fragment
from ..powers.all import Powers
from ..refs import MonsterRefResolver, resolve_power_ref
from .monster_link import monster_button, monster_link, monster_statblock
from .power_link import power_link


class FoeFoundryMdExtension(Extension):
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
            LinkPreprocessor(
                md, self.base_url, self.ref_resolver, self.resolved_refences
            ),
            "monster_link",
            175,
        )


class LinkPreprocessor(Preprocessor):
    LINK_RE = re.compile(r"\[\[(?P<name1>.+?)\]\]|\*\*(?P<name2>.+?)\*\*")
    BUTTON_RE = re.compile(r"\[\[\$(?P<name3>.+?)\]\]")
    EMBED_RE = re.compile(r"\[\[!(?P<name4>.+?)\]\]")
    NEWSLETTER_RE = re.compile(r"\[\[\@(?P<text>.+?)\]\]")

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
            new_line = self.EMBED_RE.sub(self.replace_embed, line)
            new_line = self.NEWSLETTER_RE.sub(self.replace_newsletter, new_line)
            new_line = self.BUTTON_RE.sub(self.replace_button, new_line)
            new_line = self.LINK_RE.sub(self.replace_link, new_line)

            new_lines.append(new_line)
        return new_lines

    def replace_link(self, match: re.Match):
        if match.group("name1"):
            entity_name = match.group("name1")
        elif match.group("name2"):
            entity_name = match.group("name2")
        else:
            raise ValueError("No monster name found in match")

        monster_ref = self.ref_resolver.resolve_monster_ref(entity_name)
        if monster_ref is not None:
            self.resolved_references.append(monster_ref)
            return str(monster_link(monster_ref, self.base_url))

        power = resolve_power_ref(entity_name)
        if power is not None:
            self.resolved_references.append(power)
            return str(power_link(power, self.base_url))

        return f"<b>{entity_name}</b>"

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

    def replace_embed(self, match: re.Match):
        if match.group("name4"):
            entity_name = match.group("name4")
        else:
            raise ValueError("No monster name found in match")

        monster_ref = self.ref_resolver.resolve_monster_ref(entity_name)
        if monster_ref is not None:
            self.resolved_references.append(monster_ref)
            return str(monster_statblock(monster_ref))

        power = resolve_power_ref(entity_name)
        if power is not None:
            self.resolved_references.append(power)
            power_model = Powers.PowerLookup.get(power.key)
            if power_model is None:
                raise ValueError(f"Power {power.key} not found in PowerLookup")
            return render_power_fragment(power_model)

        return match.group(0)

    def replace_newsletter(self, match: re.Match):
        if match.group("text"):
            text = match.group("text")
        else:
            raise ValueError("No text found in match")

        return f"""<div class="email-subscribe burnt-parchment m-3">
        <div class="m-3 p-3">
            <h2>{text}</h2>
            <p>Get the latest updates on new features, monsters, powers, and GM tips - all for free!</p>
            <form action="https://buttondown.com/api/emails/embed-subscribe/cordialgerm" method="post" target="popupwindow"
                onsubmit="window.open('https://buttondown.com/cordialgerm', 'popupwindow')" class="embeddable-buttondown-form">
                <div class="form-group row">
                <label for="bd-email" class="col-sm-3 col-form-label">Enter your email</label>
                <div class="col-sm-6">
                    <input type="email" name="email" id="bd-email" class="form-control" />
                </div>
                <div class="col-sm-3">
                    <button type="submit" class="btn btn-primary mb-2">Subscribe</button>
                </div>
                </div>
            </form>
        </div>
        </div>"""

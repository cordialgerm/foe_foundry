import re

from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor

from foe_foundry.utils.env import get_base_url

from ..icons import inline_icon
from ..jinja import render_power_fragment
from ..powers.all import Powers
from ..refs import MonsterRefResolver, resolve_power_ref
from .monster_link import monster_button, monster_link, monster_statblock
from .power_link import power_link


class FoeFoundryMdExtension(Extension):
    def __init__(self, **kwargs):
        self.config = {}
        self.ref_resolver = MonsterRefResolver()
        self.resolved_references = []

        base_url = get_base_url()
        self.base_url = base_url

        super().__init__(**kwargs)

    def extendMarkdown(self, md):
        md.preprocessors.register(
            MonsterSpecPreprocessor(
                md, self.base_url, self.ref_resolver, self.resolved_references
            ),
            "monster_spec",
            150,
        )
        md.preprocessors.register(
            LinkPreprocessor(
                md, self.base_url, self.ref_resolver, self.resolved_references
            ),
            "monster_link",
            175,
        )


class LinkPreprocessor(Preprocessor):
    LINK_BOLD_RE = re.compile(r"\*\*(?P<name>.+?)\*\*")
    LINK_SPECIAL_RE = re.compile(r"\[\[(?P<name>.+?)\]\]")
    BUTTON_RE = re.compile(r"\[\[\$(?P<name3>.+?)\]\]")
    EMBED_RE = re.compile(r"\[\[!(?P<name4>.+?)\]\]")
    NEWSLETTER_RE = re.compile(r"\[\[\@(?P<text>.+?)\]\]")
    HEADER_RE = re.compile(r"^(?P<hashes>#{1,6})\s+(?P<text>.+)")

    def __init__(
        self,
        md,
        base_url: str,
        ref_resolver: MonsterRefResolver,
        resolved_references: list,
    ):
        super().__init__(md)
        self.base_url = base_url
        self.ref_resolver = ref_resolver
        self.resolved_references = resolved_references
        self.current_heading_level = 1

    def run(self, lines):
        new_lines = []
        for line in lines:
            # Check if this line is a markdown header
            header_match = self.HEADER_RE.match(line)
            if header_match:
                self.current_heading_level = len(header_match.group("hashes"))

            new_line = self.EMBED_RE.sub(self.replace_embed, line)
            new_line = self.NEWSLETTER_RE.sub(self.replace_newsletter, new_line)
            new_line = self.BUTTON_RE.sub(self.replace_button, new_line)
            new_line = self.LINK_BOLD_RE.sub(self.replace_link, new_line)
            new_line = self.LINK_SPECIAL_RE.sub(self.replace_link_required, new_line)
            new_lines.append(new_line)
        return new_lines

    def _replace_link(self, match: re.Match, require_match: bool = False):
        if match.group("name"):
            entity_name = match.group("name")
        else:
            raise ValueError("No entity name found in match")

        monster_ref = self.ref_resolver.resolve_monster_ref(entity_name)

        if monster_ref is not None:
            self.resolved_references.append(monster_ref)
            return str(monster_link(monster_ref, self.base_url))

        power = resolve_power_ref(entity_name)
        if power is not None:
            self.resolved_references.append(power)
            return str(power_link(power, self.base_url))

        if require_match and (monster_ref is None and power is None):
            raise ValueError(
                f"Could not resolve reference for {entity_name}. "
                "Ensure the name is correct and the reference exists."
            )

        return f"<b>{entity_name}</b>"

    def replace_link(self, match: re.Match):
        return self._replace_link(match)

    def replace_link_required(self, match: re.Match):
        return self._replace_link(match, require_match=True)

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

            header_tag = f"h{self.current_heading_level + 1}"
            return render_power_fragment(power_model, header_tag=header_tag)

        icon = inline_icon(entity_name)
        if icon is not None:
            return str(icon)

        return match.group(0)

    def replace_newsletter(self, match: re.Match):
        if match.group("text"):
            text = match.group("text")
        else:
            raise ValueError("No text found in match")

        # Use the new EmailSubscribeCallout custom element instead of Jinja template
        return f'<email-subscribe-callout cta="{text}"></email-subscribe-callout>'


class MonsterSpecPreprocessor(Preprocessor):
    MONSTER_SPEC_RE = re.compile(r"```yaml\s*\n(?P<yaml>[\s\S]*?)```", re.MULTILINE)

    def __init__(
        self,
        md,
        base_url: str,
        ref_resolver: MonsterRefResolver,
        resolved_references: list,
    ):
        super().__init__(md)
        self.base_url = base_url
        self.ref_resolver = ref_resolver
        self.resolved_references = resolved_references

    def run(self, lines):
        # Reconstruct full markdown text
        text = "\n".join(lines)
        new_text = self.MONSTER_SPEC_RE.sub(self.replace_yaml_block, text)
        return new_text.splitlines(keepends=False)

    def replace_yaml_block(self, match: re.Match):
        if match.group("yaml"):
            monster_ref = self.ref_resolver.resolve_monster_spec(match.group("yaml"))
            if monster_ref is not None:
                self.resolved_references.append(monster_ref)
                return str(monster_statblock(monster_ref))

        return match.group(0)  # Return the original text if no match is found

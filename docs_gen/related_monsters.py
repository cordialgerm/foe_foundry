import logging
import os

import numpy as np
from mkdocs.structure.pages import Page

from foe_foundry.utils.rng import rng_from_key
from foe_foundry_data.markdown import markdown as render_markdown
from foe_foundry_data.markdown import monster_link
from foe_foundry_data.refs import MonsterRef

log = logging.getLogger("mkdocs")


def set_related_monsters_on_page(page: Page, markdown: str):
    # allow pages to opt out of this feature

    hidden = page.meta.get("hide", [])
    if isinstance(hidden, list) and "related_monsters" in hidden:
        return

    # do another rendering pass on the markdown just to find referenced monsters
    # we're going to discard the actual rendered markdown, we just want to see the references
    rendered_markdown = render_markdown(markdown)

    base_url = os.environ.get("SITE_URL")
    if base_url is None:
        raise ValueError("SITE_URL environment variable is not set.")
    if base_url.endswith("/"):
        base_url = base_url[:-1]

    monster_refs = [
        r for r in rendered_markdown.references if isinstance(r, MonsterRef)
    ]

    if len(monster_refs) == 0:
        return

    links_dict: dict[str, str] = {}

    for monster_ref in monster_refs:
        resolved_ref = monster_ref.resolve()
        name = resolved_ref.monster.key  # type: ignore  - known to be non null
        link = monster_link(resolved_ref, base_url)
        if link is None:
            continue

        links_dict[name] = str(link)

    # sort links by name
    monster_names, links = [], []
    for monster_name, link in sorted(links_dict.items()):
        monster_names.append(monster_name)
        links.append(link)

    sorted_indexes = np.argsort(monster_names)
    sorted_links = np.array(links)[sorted_indexes]

    options = [
        "**Need more inspiration?** [Browse Foe Foundry's full monster library]({base_url}/monsters/) and summon something unforgettable.",
        "**Looking for your next villain?** [Explore hundreds of handcrafted monsters]({base_url}/monsters/) built to surprise and challenge your players.",
        "**Want more like this?** [Dive into the full monster index]({base_url}/monsters/) and discover your next favorite foe.",
        "**Don't stop here.** [Check out the rest of our monsters]({base_url}/monsters/) and find something wicked for your world.",
        "**Prepare for anything.** [Browse all monsters by theme, tier, or environment]({base_url}/monsters/) and stay one step ahead of your players.",
        "**Short on time?** [Summon the perfect monster in seconds]({base_url}/monsters/) from our growing collection of free statblocks.",
        "**Build your next encounter.** [Find monsters that hit hard and ooze flavor]({base_url}/monsters/) - only some are actually oozes!",
        "**From undead horrors to celestial tyrants,** [our monster page has it all]({base_url}/monsters/). You never know what you'll summon next.",
        "**No boring statblocks here.** [Explore monsters packed with flavor and firepower]({base_url}/monsters/) and keep your players guessing.",
        "**Prep smarter.** [Browse Foe Foundry's monster vault]({base_url}/monsters/) and let us inspire you for your next session.",
    ]
    rng = rng_from_key(page.file.abs_dest_path)
    i = rng.choice(len(options))
    related_monster_cta = render_markdown(options[i].format(base_url=base_url)).html

    page.meta["related_monsters"] = sorted_links
    page.meta["related_monster_cta"] = related_monster_cta

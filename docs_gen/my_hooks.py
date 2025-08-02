import logging
from datetime import datetime
from typing import Optional

from mkdocs.config.defaults import MkDocsConfig
from mkdocs.structure.files import Files
from mkdocs.structure.pages import Page

from docs_gen.backlinks import BlogBacklinks
from docs_gen.json_ld import set_json_ld_on_page
from docs_gen.related_monsters import set_related_monsters_on_page
from foe_foundry_data.homepage import load_homepage_data
from foe_foundry_data.jinja.env import setup_jinja_env
from foe_foundry_data.markdown import create_newsletter

log = logging.getLogger("mkdocs")
backlinks = BlogBacklinks(log)


def on_config(config, **kwargs):
    config.copyright = (
        f"Copyright © {datetime.now().year} Evan Rash. All Rights Reserved."
    )


def on_files(files: Files, *, config: MkDocsConfig) -> Optional[Files]:
    backlinks.on_files(files, config=config)


def on_page_context(context, page: Page, config, nav):
    set_json_ld_on_page(page)
    backlinks.on_page_context(context, page, config, nav)

    homepage_data = load_homepage_data()

    context["default_monster_key"] = homepage_data.monsters[0].key

    if page.is_homepage:
        context["homepage_data"] = homepage_data


def on_page_markdown(markdown: str, page: Page, config, files):
    set_related_monsters_on_page(page, markdown)


def on_page_content(html, page, config, files):
    backlinks.on_page_content(html, page, config, files)


def on_env(env, config, files):
    env.globals["render_newsletter"] = create_newsletter
    setup_jinja_env(env)
    return env

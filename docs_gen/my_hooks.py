import logging
from datetime import datetime

from mkdocs.structure.pages import Page

from docs_gen.json_ld import set_json_ld_on_page
from docs_gen.related_monsters import set_related_monsters_on_page

log = logging.getLogger("mkdocs")


def on_config(config, **kwargs):
    config.copyright = (
        f"Copyright © {datetime.now().year} Evan Rash. All Rights Reserved."
    )


def on_page_context(context, page: Page, config, nav):
    set_json_ld_on_page(page)


def on_page_markdown(markdown: str, page: Page, config, files):
    set_related_monsters_on_page(page, markdown)

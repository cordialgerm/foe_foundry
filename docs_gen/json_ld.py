import json
import logging
from datetime import datetime

from mkdocs.structure.pages import Page
from mkdocs_blogging_plugin.util import Util as BloggingUtil

from foe_foundry.utils.env import get_base_url

log = logging.getLogger("mkdocs")


def set_json_ld_on_page(page: Page):
    base_url = get_base_url()

    def image_url(path: str = "") -> str:
        if path is None or path == "":
            return image_url("img/icons/favicon.webp")

        if path.startswith("/"):
            path = path[1:]

        return f"{base_url}/{path}"

    util = BloggingUtil()

    meta = page.meta

    # only attach the json_ld metadata to posts that opt in
    if not meta.get("json_ld", False):
        return

    headline = meta.get("short_title", meta.get("title", ""))
    description = meta.get("description", "")
    image = image_url(meta.get("image", ""))

    modified_time = page.meta.get("modified_time_localized")
    if modified_time is None:
        git_timestamp = util.get_git_commit_timestamp(
            page.file.abs_src_path, is_first_commit=False
        )
        modified_time = datetime.fromtimestamp(git_timestamp)
        modified_time_localized = modified_time.isoformat()
        page.meta["modified_time_localized"] = modified_time_localized

    published_time = page.meta.get("published_time_localized")
    if published_time is None:
        git_timestamp = util.get_git_commit_timestamp(
            page.file.abs_src_path, is_first_commit=True
        )
        published_time = datetime.fromtimestamp(git_timestamp)
        published_time_localized = published_time.isoformat()
        page.meta["published_time_localized"] = published_time_localized

    json_ld = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": headline,
        "description": description,
        "image": image,
        "author": {"@type": "Person", "name": "Evan Rash"},
        "publisher": {
            "@type": "Organization",
            "name": "Foe Foundry",
            "logo": {
                "@type": "ImageObject",
                "url": image_url(),
            },
        },
        "datePublished": published_time_localized,
        "dateModified": modified_time_localized,
        "mainEntityOfPage": {
            "@type": "WebPage",
            "@id": f"{base_url}/{page.url}",
        },
    }
    page.meta["json_ld"] = json.dumps(json_ld, indent=2)

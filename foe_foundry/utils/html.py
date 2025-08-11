from urllib.parse import urljoin

from bs4 import BeautifulSoup
from bs4.element import Tag


def remove_h2_sections(html: str, h2_ids_to_remove: list[str]) -> str:
    soup = BeautifulSoup(html, "html.parser")
    h2_tags = soup.find_all("h2")
    if not h2_tags:
        return html

    h2_ids_set = set(h2_ids_to_remove)
    to_remove = []
    for h2 in h2_tags:
        if not isinstance(h2, Tag):
            continue
        h2_id = h2.get("id")
        if h2_id and h2_id in h2_ids_set:
            current = h2
            to_remove.append(current)
            next_sibling = current.find_next_sibling()
            while (
                next_sibling
                and isinstance(next_sibling, Tag)
                and next_sibling.name != "h2"
            ):
                to_remove.append(next_sibling)
                next_sibling = next_sibling.find_next_sibling()

    for el in to_remove:
        if isinstance(el, Tag):
            el.decompose()

    return str(soup)


def fix_relative_paths(html: str, base_path: str) -> str:
    """
    Fix relative paths in an HTML string by rewriting them using the given base path.

    :param html: The raw HTML content as a string.
    :param base_path: The base path to prepend to relative URLs (e.g., "/docs/some-page/")
    :return: Modified HTML as a string.
    """
    soup = BeautifulSoup(html, "html.parser")

    # Tags and their relevant attributes
    tag_attr_map = {
        "a": "href",
        "img": "src",
        "script": "src",
        "link": "href",
        "source": "src",
        "iframe": "src",
    }

    skip_prefixes = ("/", "http", "https", "#", "data:")
    base_path_slash = base_path.rstrip("/") + "/"

    for tag, attr in tag_attr_map.items():
        for el in soup.find_all(tag):
            if not isinstance(el, Tag):
                continue
            val = el.get(attr)
            if isinstance(val, str) and not val.startswith(skip_prefixes):
                el[attr] = urljoin(base_path_slash, val)

    # Handle srcset manually (used in <img> or <source> tags)
    for el in soup.find_all(["img", "source"]):
        if not isinstance(el, Tag):
            continue
        srcset = el.get("srcset")
        if isinstance(srcset, str):
            new_srcset = []
            for part in srcset.split(","):
                url, *descriptor = part.strip().split(" ")
                if url and not url.startswith(skip_prefixes):
                    url = urljoin(base_path_slash, url)
                new_srcset.append(" ".join([url] + descriptor) if descriptor else url)
            el["srcset"] = ", ".join(new_srcset)

    return str(soup)

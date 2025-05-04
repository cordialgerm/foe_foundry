from urllib.parse import urljoin

from bs4 import BeautifulSoup


def remove_h2_sections(html: str, h2_ids_to_remove: list[str]) -> str:
    soup = BeautifulSoup(html, "html.parser")
    h2_tags = soup.find_all("h2")

    for h2 in h2_tags:
        if h2.get("id") in h2_ids_to_remove:  # type: ignore
            current = h2
            while True:
                next_sibling = current.find_next_sibling()
                current.decompose()
                if not next_sibling or next_sibling.name == "h2":  # type: ignore
                    break
                current = next_sibling

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

    for tag, attr in tag_attr_map.items():
        for el in soup.find_all(tag):
            val = el.get(attr)
            if val and not val.startswith(("/", "http", "https", "#", "data:")):
                new_val = urljoin(base_path + "/", val)
                el[attr] = new_val

    # Handle srcset manually (used in <img> or <source> tags)
    for el in soup.find_all(["img", "source"]):
        srcset = el.get("srcset")
        if srcset:
            new_srcset = []
            for part in srcset.split(","):
                url, *descriptor = part.strip().split(" ")
                if not url.startswith(("/", "http", "https", "data:")):
                    url = urljoin(base_path + "/", url)
                new_srcset.append(" ".join([url] + descriptor))
            el["srcset"] = ", ".join(new_srcset)

    return str(soup)

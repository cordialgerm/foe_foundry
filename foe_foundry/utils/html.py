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

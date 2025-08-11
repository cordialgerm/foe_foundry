import os
from dataclasses import dataclass
from typing import Optional

from bs4 import BeautifulSoup
from mkdocs.config.defaults import MkDocsConfig
from mkdocs.structure.files import File, Files
from mkdocs.structure.pages import Page


class LinkScraper:
    def __init__(self, html: str):
        self.html = html

    def links(self):
        """
        Scrapes the valid links from an HTML file. A valid link will not be a
        named anchor and will not point to an external page.
        :return: a list of valid links.
        """
        links = BeautifulSoup(self.html, features="html.parser").find_all("a")
        return self.__remove_invalid_links(links)

    def __remove_invalid_links(self, links):
        return [
            link
            for link in links
            if self.__has_href(link) and self.__is_valid_href(link.attrs["href"])
        ]

    def __is_valid_href(self, href: str) -> bool:
        return not self.__is_named_anchor(href) and not self.__is_external_link(href)

    def __has_href(self, link) -> bool:
        return "href" in link.attrs

    def __is_named_anchor(self, href: str) -> bool:
        return href.strip().startswith("#")

    def __is_external_link(self, href: str) -> bool:
        return href.strip().lower().startswith("http")


@dataclass
class Backlink:
    src_url: str
    src_title: str
    dst_url: str

    @property
    def key(self) -> str:
        return f"{self.src_url} -> {self.dst_url}"


class BlogBacklinks:
    def __init__(self, log):
        super().__init__()
        self.files_dict: dict[str, File] = {}
        self.log = log
        self.backlinks: list[Backlink] = []
        self.backlink_keys: set[str] = set()

    def on_files(self, files: Files, *, config: MkDocsConfig) -> Optional[Files]:
        self.files_dict = {file.url: file for file in files}
        return files

    def on_page_content(self, html: str, page: Page, config, files):
        for link in LinkScraper(html).links():
            href: str = link.attrs["href"]
            destination_link = self.__normalize_link(href, page.url)
            file = self.files_dict.get(destination_link)
            if file is None:
                continue

            url = page.url
            if not url.startswith("/"):
                url = "/" + url

            if not url.startswith("/blog/"):
                continue

            self.log.info(f"Blog {page.url} links to {file.url}")

            backlink = Backlink(
                src_url=page.url, src_title=str(page.title), dst_url=file.url
            )
            if backlink.key in self.backlink_keys:
                continue

            self.backlinks.append(backlink)
            self.backlink_keys.add(backlink.key)

        return html

    def on_page_context(self, context, page: Page, config, nav):
        backlinks = [b for b in self.backlinks if b.dst_url == page.url]

        def sort_backlinks(backlink: Backlink):
            return backlink.src_title

        backlinks.sort(key=sort_backlinks)

        hide = "backlinks" in page.meta.get("hide", [])
        if not hide:
            page.meta["backlinks"] = backlinks

        return context

    def __normalize_link(self, href: str, page_url: str) -> str:
        """
        Normalizes a link. That means:
        - Checking if links are relative or absolute.
        - Resolving their paths and normalizing them, making sure that the URLs
          are going to be valid when added to the HTML.
        - Normalization will be different, depending on the link being relative
          or absolute.
        :param href: the url scraped from the html file.
        :param page_url: the URL of the page that is linking to the href.
        :return: the normalized URL.
        """
        if self.__is_absolute_link(href):
            return self.__normalize_absolute_link(href)
        return self.__normalize_relative_link(href, page_url)

    def __normalize_relative_link(self, href: str, page_url: str) -> str:
        link = os.path.join(page_url, href)
        return os.path.normpath(link) + "/"

    def __normalize_absolute_link(self, href: str) -> str:
        link = os.path.normpath(href) + "/"
        if link.startswith("/"):
            return link[1:]
        return link

    def __is_absolute_link(self, href: str):
        return href.startswith("/")

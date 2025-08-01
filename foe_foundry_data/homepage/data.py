from dataclasses import dataclass
from datetime import datetime


@dataclass(kw_only=True)
class HomepageMonster:
    key: str
    name: str
    url: str
    image: str
    tagline: str
    transparent_edges: bool
    grayscale: bool
    background_color: str | None
    mask_css: str
    is_new: bool
    create_date: datetime
    modified_date: datetime

    @property
    def custom_style(self) -> str:
        """
        Returns a custom CSS style string for the monster's background color.
        If no background color is set, returns an empty string.
        """
        if self.background_color:
            return f'style="background-color: {self.background_color};"'
        return ""


@dataclass(kw_only=True)
class HomepagePower:
    name: str
    url: str
    icon_svg: str
    icon_url: str
    details_html: str
    mask_css: str


@dataclass
class HomepageBlog:
    name: str
    image: str
    url: str
    transparent_edges: bool
    grayscale: bool
    bg_object_css_class: str
    mask_css: str

    @property
    def use_bg_image(self) -> bool:
        return self.transparent_edges or self.grayscale


@dataclass(kw_only=True)
class HomepageData:
    monsters: list[HomepageMonster]
    powers: list[HomepagePower]
    blogs: list[HomepageBlog]

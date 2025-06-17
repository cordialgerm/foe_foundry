from dataclasses import dataclass


@dataclass(kw_only=True)
class HomepageMonster:
    name: str
    url: str
    image: str
    tagline: str
    transparent_edges: bool


@dataclass(kw_only=True)
class HomepagePower:
    name: str
    url: str
    icon_svg: str
    icon_url: str
    details_html: str


@dataclass
class HomepageBlog:
    name: str
    image: str
    url: str
    transparent_edges: bool
    grayscale: bool
    bg_object_css_class: str

    @property
    def use_bg_image(self) -> bool:
        return self.transparent_edges or self.grayscale


@dataclass(kw_only=True)
class HomepageData:
    monsters: list[HomepageMonster]
    powers: list[HomepagePower]
    blogs: list[HomepageBlog]

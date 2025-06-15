from dataclasses import dataclass


@dataclass(kw_only=True)
class HomepageMonster:
    name: str
    image: str
    tagline: str


@dataclass(kw_only=True)
class HomepagePower:
    name: str
    icon_svg: str
    details_html: str


@dataclass
class HomepageBlog:
    name: str
    image: str


@dataclass(kw_only=True)
class HomepageData:
    monsters: list[HomepageMonster]
    powers: list[HomepagePower]
    blogs: list[HomepageBlog]

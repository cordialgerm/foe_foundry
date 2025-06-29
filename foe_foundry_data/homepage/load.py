from pathlib import Path

import numpy as np
from markdown import markdown

from foe_foundry.creatures import AllTemplates, MonsterTemplate
from foe_foundry.utils.image import has_transparent_edges
from foe_foundry_data.blogs import BlogPost, load_blog_posts
from foe_foundry_data.icons import inline_icon
from foe_foundry_data.powers import PowerModel, Powers

from .data import HomepageBlog, HomepageData, HomepageMonster, HomepagePower


class _RandomMask:
    """
    A class to handle random mask selection for homepage elements.
    """

    def __init__(self, mask_count: int):
        self.mask_count = mask_count
        self.last_index = -1
        self.rng = np.random.default_rng()

    def random_mask_css(self) -> str:
        n = self.rng.choice(self.mask_count) + 1
        if n == self.last_index:
            n = (n + 1) % self.mask_count
        self.last_index = n
        return f"masked v{n}"


def load_homepage_data() -> HomepageData:
    """
    Load the homepage data from the data module.

    Returns:
        HomepageData: An instance of HomepageData containing monsters, powers, and blogs.
    """

    rng = np.random.default_rng(20240711)

    mask_dir = Path.cwd() / "docs" / "img" / "backgrounds" / "masks"

    # check for webp or png
    mask_count = len(list(mask_dir.glob("*.webp"))) + len(list(mask_dir.glob("*.png")))
    random_mask = _RandomMask(mask_count)

    powers = [
        _power(p, random_mask.random_mask_css())
        for _, p in Powers.PowerLookup.items()
        if len(p.feature_descriptions) <= 400
    ]
    monsters = [
        _monster(m, random_mask.random_mask_css())
        for m in AllTemplates
        if m.lore_md is not None
    ]
    blogs = load_blog_posts()

    rng.shuffle(powers)  # type: ignore
    rng.shuffle(monsters)  # type: ignore

    return HomepageData(
        monsters=monsters,
        powers=powers,
        blogs=[_blog(b, rng, random_mask.random_mask_css()) for b in blogs],
    )


def _blog(blog: BlogPost, rng: np.random.Generator, mask_css: str) -> HomepageBlog:
    bg_objects_dir = Path.cwd() / "docs" / "img" / "backgrounds" / "objects"
    bg_objects = [f for f in bg_objects_dir.glob("*.webp")]

    bg_object: Path = rng.choice(bg_objects)  # type: ignore

    css_class = bg_object.stem

    return HomepageBlog(
        name=blog.title,
        url=blog.url,
        image=blog.image,
        grayscale=blog.image_is_grayscaleish,
        transparent_edges=blog.image_has_transparent_edges,
        bg_object_css_class=css_class,
        mask_css=mask_css,
    )


def _monster(monster: MonsterTemplate, mask_css: str) -> HomepageMonster:
    if monster.primary_image_url is None:
        image = "img/icons/favicon.webp"
        transparent = True
    else:
        rel_to = Path(__file__).parent.parent.parent / "docs"
        image = str(monster.primary_image_url.relative_to(rel_to))
        transparent = has_transparent_edges(monster.primary_image_url)

    return HomepageMonster(
        name=monster.name,
        url=f"monsters/{monster.key}/",
        image=image,
        tagline=monster.tag_line,
        transparent_edges=transparent,
        mask_css=mask_css,
    )


def _power(power: PowerModel, mask_css: str) -> HomepagePower:
    feature_descriptions_html = markdown(power.feature_descriptions)

    icon = inline_icon(power.icon or "favicon", fill="currentColor", wrap=False)
    if icon is None:
        raise ValueError(f"Power {power.name} has no icon")

    return HomepagePower(
        name=power.name,
        url=f"powers/{power.theme.lower()}/#{power.key}",
        icon_svg=str(icon),
        icon_url=f"img/icons/{power.icon}.svg",
        details_html=feature_descriptions_html,
        mask_css=mask_css,
    )

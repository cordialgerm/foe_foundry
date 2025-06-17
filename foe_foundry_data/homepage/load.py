from pathlib import Path

import numpy as np
from markdown import markdown

from foe_foundry.creatures import AllTemplates, MonsterTemplate
from foe_foundry.utils.image import has_transparent_edges
from foe_foundry_data.blogs import BlogPost, load_blog_posts
from foe_foundry_data.icons import inline_icon
from foe_foundry_data.powers import PowerModel, Powers

from .data import HomepageBlog, HomepageData, HomepageMonster, HomepagePower


def load_homepage_data() -> HomepageData:
    """
    Load the homepage data from the data module.

    Returns:
        HomepageData: An instance of HomepageData containing monsters, powers, and blogs.
    """

    rng = np.random.default_rng(20240711)

    powers = [
        _power(p)
        for _, p in Powers.PowerLookup.items()
        if len(p.feature_descriptions) <= 400
    ]
    monsters = [_monster(m) for m in AllTemplates if m.lore_md is not None]
    blogs = load_blog_posts()

    rng.shuffle(powers)  # type: ignore
    rng.shuffle(monsters)  # type: ignore

    return HomepageData(
        monsters=monsters,
        powers=powers,
        blogs=[_blog(b, rng) for b in blogs],
    )


def _blog(blog: BlogPost, rng: np.random.Generator) -> HomepageBlog:
    bg_objects_dir = Path.cwd() / "docs" / "img" / "backgrounds" / "objects"
    bg_objects = [f for f in bg_objects_dir.glob("*.webp")]

    bg_object: Path = rng.choice(bg_objects)  # type: ignore

    css_class = bg_object.stem

    return HomepageBlog(
        name=blog.title,
        image=blog.image,
        grayscale=blog.image_is_grayscaleish,
        transparent_edges=blog.image_has_transparent_edges,
        bg_object_css_class=css_class,
    )


def _monster(monster: MonsterTemplate) -> HomepageMonster:
    if monster.primary_image_url is None:
        image = "img/icons/favicon.webp"
        transparent = True
    else:
        rel_to = Path(__file__).parent.parent.parent / "docs"
        image = str(monster.primary_image_url.relative_to(rel_to))
        transparent = has_transparent_edges(monster.primary_image_url)

    return HomepageMonster(
        name=monster.name,
        image=image,
        tagline=monster.tag_line,
        transparent_edges=transparent,
    )


def _power(power: PowerModel) -> HomepagePower:
    feature_descriptions_html = markdown(power.feature_descriptions)

    icon = inline_icon(power.icon or "favicon")
    if icon is None:
        raise ValueError(f"Power {power.name} has no icon")

    return HomepagePower(
        name=power.name, icon_svg=str(icon), details_html=feature_descriptions_html
    )

from pathlib import Path

from markdown import markdown

from foe_foundry.creatures import AllTemplates, MonsterTemplate
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

    powers = [_power(p) for _, p in Powers.PowerLookup.items()]
    monsters = [_monster(m) for m in AllTemplates]
    blogs = load_blog_posts()

    return HomepageData(
        monsters=monsters,
        powers=powers,
        blogs=[_blog(b) for b in blogs],
    )


def _blog(blog: BlogPost) -> HomepageBlog:
    return HomepageBlog(name=blog.title, image=blog.image)


def _monster(monster: MonsterTemplate) -> HomepageMonster:
    if monster.primary_image_url is None:
        image = "img/icons/favicon.webp"
    else:
        rel_to = Path(__file__).parent.parent.parent / "docs"
        image = str(monster.primary_image_url.relative_to(rel_to))

    return HomepageMonster(name=monster.name, image=image, tagline=monster.tag_line)


def _power(power: PowerModel) -> HomepagePower:
    feature_descriptions_html = markdown(power.feature_descriptions)

    icon = inline_icon(power.icon or "favicon")
    if icon is None:
        raise ValueError(f"Power {power.name} has no icon")

    return HomepagePower(
        name=power.name, icon_svg=str(icon), details_html=feature_descriptions_html
    )

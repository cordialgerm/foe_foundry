from functools import cached_property
from pathlib import Path

import numpy as np
import pandas as pd
from markdown import markdown

from foe_foundry_data.blogs import BlogPost, load_blog_posts
from foe_foundry_data.icons import inline_icon
from foe_foundry_data.monsters import MonsterModel
from foe_foundry_data.monsters.all import Monsters
from foe_foundry_data.powers import PowerModel, Powers

from ..mask import random_mask
from .data import HomepageBlog, HomepageData, HomepageMonster, HomepagePower


class _HomepageDataCache:
    @cached_property
    def load_homepage_data(self) -> HomepageData:
        """
        Load the homepage data from the data module.

        Returns:
            HomepageData: An instance of HomepageData containing monsters, powers, and blogs.
        """
        rng = np.random.default_rng(20240711)
        powers = [
            _power(p, random_mask.random_mask_css())
            for _, p in Powers.PowerLookup.items()
            if len(p.feature_descriptions) <= 400
        ]

        # note - Monster.one_of_each_monster has one of each monster
        #        we just want one example per template
        template_keys = set()
        monsters = []
        for m in Monsters.one_of_each_monster:
            if m.has_lore and m.template_name not in template_keys:
                template_keys.add(m.template_name)
                monsters.append(_monster(m, random_mask.random_mask_css()))

        # Create a DataFrame for sorting
        df = pd.DataFrame(
            {
                "monster": monsters,
                "monster_name": [m.name for m in monsters],
                "create_date": [m.create_date for m in monsters],
            }
        )

        # Sort by create_date descending, then monster_name ascending
        df_sorted = df.sort_values(
            ["create_date", "monster_name"], ascending=[False, True]
        )

        # Enhanced logic: mark the most recent published monsters as new
        # If there are multiple monsters published on the same day, include those, up to 10
        # Otherwise, the most recent 3 monsters will be shown
        if not df_sorted.empty:
            most_recent_date = df_sorted.iloc[0]["create_date"].date()
            most_recent_publish_count = (
                df_sorted["create_date"]
                .apply(lambda d: d.date() == most_recent_date)
                .sum()
            )
            cap = min(max(3, most_recent_publish_count), 10)
            # Mark the first 'cap' monsters as new
            for m in df_sorted.head(cap)["monster"]:
                m.is_new = True

        # Rebuild monsters list: new first, then shuffle the rest
        new_monsters = sorted(
            [m for m in monsters if m.is_new], key=lambda m: m.create_date, reverse=True
        )
        old_monsters = [m for m in monsters if not m.is_new]
        rng.shuffle(old_monsters)  # type: ignore
        monsters = new_monsters + old_monsters

        blogs = load_blog_posts()

        rng.shuffle(powers)  # type: ignore

        # when shuffling monsters, start with the newest ones first, then shuffle the rest
        # this ensures that the newest monsters are always shown first
        # we shuffle the rest to ensure variety for things like SEO indexing
        new_monsters = [m for m in monsters if m.is_new]
        old_monsters = [m for m in monsters if not m.is_new]
        rng.shuffle(old_monsters)  # type: ignore

        monsters = new_monsters + old_monsters

        return HomepageData(
            monsters=monsters,
            powers=powers,
            blogs=[_blog(b, rng, random_mask.random_mask_css()) for b in blogs],
        )


_cache = _HomepageDataCache()


def load_homepage_data() -> HomepageData:
    """
    Load the homepage data from the cache or create it if not already cached.

    Returns:
        HomepageData: An instance of HomepageData containing monsters, powers, and blogs.
    """
    return _cache.load_homepage_data


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


def _monster(monster: MonsterModel, mask_css: str) -> HomepageMonster:
    return HomepageMonster(
        key=monster.key,
        name=monster.template_name,
        template=monster.template_key,
        url=f"monsters/{monster.template_key}/",
        image=monster.primary_image or "img/icons/favicon.webp",
        tagline=monster.tag_line,
        transparent_edges=monster.primary_image_has_transparent_edges,
        grayscale=monster.primary_image_is_grayscaleish,
        background_color=monster.primary_image_background_color,
        mask_css=mask_css,
        create_date=monster.create_date,
        is_new=False,  # temporary, will determine which are considered "new" based on creation dates of all monsters
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

from functools import cached_property
from pathlib import Path

from foe_foundry.utils.image import has_transparent_edges
from foe_foundry.utils.monster_content import extract_yaml_frontmatter

from .data import BlogPost


class _Loader:
    @cached_property
    def blog_posts(self) -> list[BlogPost]:
        root_dir = Path(__file__).parent.parent.parent / "docs"
        blog_dir = root_dir / "blog"

        posts = []
        for file in blog_dir.glob("*.md"):
            if file.name in {"index.md", "tags.md"}:
                continue
            try:
                with open(file, encoding="utf-8") as f:
                    content = f.read()

                frontmatter = extract_yaml_frontmatter(content)
                title = frontmatter.get("short_title", frontmatter["title"])
                description = frontmatter.get("description", title)
                url = file.relative_to(root_dir).as_posix()
                image = frontmatter.get("image", "img/icons/favicon.webp")
                date = frontmatter["date"]

                transparent = has_transparent_edges(Path.cwd() / "docs" / image)

                posts.append(
                    BlogPost(
                        title=title,
                        description=description,
                        url=url,
                        image=image,
                        date=date,
                        image_has_transparent_edges=transparent,
                    )
                )
            except Exception as e:
                raise ValueError(f"Error processing blog post {file}: {e}") from e

        return sorted(posts, key=lambda post: post.date, reverse=True)


_loader = _Loader()


def load_blog_posts() -> list[BlogPost]:
    """Load metadata about blog posts"""
    return _loader.blog_posts

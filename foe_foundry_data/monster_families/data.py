from __future__ import annotations

from pathlib import Path
from urllib.parse import urljoin

from foe_foundry.creatures import AllTemplates
from foe_foundry.utils import name_to_key
from foe_foundry.utils.env import get_base_url
from foe_foundry.utils.image import (
    get_dominant_edge_color,
    has_transparent_edges,
    is_grayscaleish,
)
from foe_foundry.utils.monster_content import (
    extract_monster_hyperlinks,
    extract_yaml_frontmatter,
    strip_yaml_frontmatter,
)

from ..base import MonsterFamilyInfo, MonsterTemplateInfoModel
from ..refs import MonsterRefResolver

ref_resolver = MonsterRefResolver()


def _convert_template_to_info_model(template, base_url: str) -> MonsterTemplateInfoModel:
    """Convert a MonsterTemplate to MonsterTemplateInfoModel."""
    if base_url.endswith("/"):
        base_url = base_url[:-1]

    # Convert image path to absolute URL
    if template.primary_image_url is not None:
        relative_image = template.primary_image_url.relative_to(Path.cwd() / "docs").as_posix()
        absolute_image = urljoin(base_url, relative_image)
        
        # Get image properties
        transparent_edges = has_transparent_edges(template.primary_image_url)
        if not transparent_edges:
            grayscale = is_grayscaleish(template.primary_image_url)
            background_color = get_dominant_edge_color(template.primary_image_url)
        else:
            grayscale = False
            background_color = None
            
        # Construct mask CSS
        mask_css = f"mask-image: url('{absolute_image}')" if transparent_edges else ""
    else:
        absolute_image = ""
        transparent_edges = False
        grayscale = False
        background_color = None
        mask_css = ""

    return MonsterTemplateInfoModel(
        key=template.key,
        name=template.name,
        url=f"/monsters/{template.key}/",
        image=absolute_image,
        tagline=template.tag_line,
        transparent_edges=transparent_edges,
        grayscale=grayscale,
        background_color=background_color,
        mask_css=mask_css,
        is_new=False,  # TODO: Determine how to calculate this
        create_date=template.create_date,
    )


def load_monster_families() -> list[MonsterFamilyInfo]:
    """Load monster families from markdown files."""
    families_dir = Path.cwd() / "docs" / "families"
    base_url = get_base_url()
    
    families = []
    for md_file in families_dir.glob("*.md"):
        family = _load_family_from_file(md_file, base_url)
        if family is not None:
            families.append(family)
    
    return families


def _load_family_from_file(md_file: Path, base_url: str) -> MonsterFamilyInfo | None:
    """Create MonsterFamilyInfo from a markdown file."""
    with md_file.open() as f:
        content = f.read()
        
    frontmatter = extract_yaml_frontmatter(content)
    is_monster_family = frontmatter.get("is_monster_family", False)
    if not is_monster_family:
        return None
        
    key = name_to_key(md_file.stem)
    name = frontmatter.get("short_title", frontmatter.get("title"))
    icon = frontmatter.get("icon")
    
    if not isinstance(name, str):
        raise ValueError(f"Invalid title for family '{key}': {name}. Expected a string.")
    
    if not isinstance(icon, str):
        raise ValueError(f"Icon not found for family '{key}'. Ensure it is defined in the YAML frontmatter.")
    
    markdown_content = strip_yaml_frontmatter(content)
    monster_links = extract_monster_hyperlinks(markdown_content)

    # Get unique templates from monster links
    template_keys: set[str] = set()
    for link in monster_links:
        ref = ref_resolver.resolve_monster_ref(link)
        if ref is None:
            raise ValueError(f"Monster reference '{link}' in family '{name}' could not be resolved.")
        template = ref.template
        template_keys.add(template.key)

    # Convert templates to info models
    templates = []
    for template in AllTemplates:
        if template.key in template_keys:
            template_info = _convert_template_to_info_model(template, base_url)
            templates.append(template_info)

    return MonsterFamilyInfo(key=key, name=name, icon=icon, templates=templates)
"""Tags API routes."""

from typing import Annotated

from fastapi import APIRouter, HTTPException, Query

from foe_foundry.utils import name_to_key
from foe_foundry_data.tags import TagInfoModel, Tags

router = APIRouter(prefix="/api/v1/tags")


@router.get("/tag/{tag_key}")
def get_tag(*, tag_key: str) -> TagInfoModel:
    """Get detailed information about a specific tag including example monsters"""
    # Try direct lookup first (for keys like "tier_0")
    tag = Tags.TagLookup.get(tag_key)
    if tag is None:
        # Try with name_to_key conversion (for names like "Tier 0" -> "tier_0")
        key = name_to_key(tag_key)
        tag = Tags.TagLookup.get(key)
    if tag is None:
        # Try lookup by display name (for names like "Tier 0")
        for tag_info in Tags.AllTags:
            if tag_info.name.lower() == tag_key.lower():
                tag = tag_info
                break
    if tag is None:
        raise HTTPException(status_code=404, detail="Tag not found")
    return tag


@router.get("/all")
def all_tags(
    *,
    category: Annotated[str | None, Query(title="Filter by tag category")] = None,
) -> list[TagInfoModel]:
    """Get all available tags, optionally filtered by category"""
    tags = Tags.AllTags

    if category:
        tags = [tag for tag in tags if tag.category.lower() == category.lower()]

    return tags


@router.get("/categories")
def get_categories() -> list[str]:
    """Get all available tag categories"""
    categories = set(tag.category for tag in Tags.AllTags)
    return sorted(categories)

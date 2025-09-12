from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse, RedirectResponse
from starlette.datastructures import URL

from foe_foundry_data.refs import MonsterRefResolver

router = APIRouter()
ref_resolver = MonsterRefResolver()


def find_monster(slug: str) -> tuple[str, str] | None:
    """
    Return (template_slug, monster_key) if this slug is a monster-key.
    Otherwise return None.
    """
    slug = slug.strip().lower()
    ref = ref_resolver.resolve_monster_ref(slug)
    if ref is None:
        return None

    # If we found a reference and it has a monster (not just a template)
    if ref.monster is not None:
        return ref.template.key, ref.monster.key

    return None


def _template_index(site_dir: Path, slug: str) -> Path:
    return site_dir / "monsters" / slug / "index.html"


@router.get("/monsters/{slug}/", include_in_schema=False)
@router.get("/monsters/{slug}", include_in_schema=False)
async def monsters_pretty_router(slug: str, request: Request):
    site_dir: Path = request.app.state.site_dir

    # 1. Check for static template page
    index_path = _template_index(site_dir, slug)
    if index_path.is_file():
        return FileResponse(index_path)

    # 2. Check for monster key
    match = find_monster(slug)
    if match:
        template_slug, monster_key = match
        base = str(
            URL(str(request.url)).replace(
                path=f"/monsters/{template_slug}/", query="", fragment=""
            )
        )
        return RedirectResponse(url=f"{base}#{monster_key}", status_code=302)

    # 3. Nothing found
    raise HTTPException(status_code=404, detail="Monster or template not found")

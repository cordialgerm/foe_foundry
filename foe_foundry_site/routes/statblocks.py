from __future__ import annotations

import os
from dataclasses import asdict
from enum import StrEnum
from typing import Annotated

import numpy as np
from fastapi import APIRouter, Body, HTTPException, Query, Response
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

from foe_foundry.creatures import (
    random_template_and_settings,
)
from foe_foundry.statblocks import Statblock
from foe_foundry_data.generate import generate_monster
from foe_foundry_data.jinja import render_statblock_markdown
from foe_foundry_data.monsters import MonsterModel
from foe_foundry_data.refs import MonsterRefResolver

from .data import MonsterMeta

router = APIRouter(prefix="/api/v1/statblocks")
ref_resolver = MonsterRefResolver()


class StatblockFormat(StrEnum):
    html = "html"
    monster_only = "monster_only"
    json = "json"
    md_5esrd = "md_5esrd"
    md_gmbinder = "md_gmbinder"
    md_homebrewery = "md_homebrewery"
    md_blackflag = "md_blackflag"

    @staticmethod
    def All():
        return [
            StatblockFormat.html,
            StatblockFormat.monster_only,
            StatblockFormat.json,
            StatblockFormat.md_5esrd,
            StatblockFormat.md_gmbinder,
            StatblockFormat.md_homebrewery,
            StatblockFormat.md_blackflag,
        ]


class StatblockGenerationRequest(BaseModel):
    monster_key: str
    powers: list[str] | None = None
    hp_multiplier: float | None = None
    damage_multiplier: float | None = None


@router.get("/random")
def random_statblock(
    output: Annotated[
        StatblockFormat | None,
        Query(title="return format", examples=StatblockFormat.All()),
    ] = None,
) -> Response:
    rng = np.random.default_rng()
    template, settings = random_template_and_settings(
        rng=rng,
        filter_templates=None,
        filter_variants=None,
        filter_monsters=None,
        species_filter=None,
    )

    stats = template.generate(settings).finalize()

    if output is None:
        output = StatblockFormat.html

    base_url = os.environ.get("SITE_URL")
    if base_url is None:
        raise ValueError("SITE_URL environment variable is not set")
    monster_model = MonsterModel.from_monster(
        stats=stats,
        template=template,
        variant=settings.variant,
        monster=settings.monster,
        species=settings.species,
        base_url=base_url,
    )
    return _format_statblock(
        monster_model=monster_model, stats=stats, rng=rng, output=output
    )


@router.get("/{template_or_variant_key}")
def get_statblock(
    template_or_variant_key: str,
    output: Annotated[
        StatblockFormat | None,
        Query(title="return format", examples=StatblockFormat.All()),
    ] = None,
):
    rng = np.random.default_rng()
    ref, stats = generate_monster(
        template_or_variant_key, ref_resolver=ref_resolver, rng=rng
    )

    if stats is None or ref is None:
        raise HTTPException(
            status_code=404, detail=f"Monster not found: {template_or_variant_key}"
        )
    base_url = os.environ.get("SITE_URL")
    if base_url is None:
        raise ValueError("SITE_URL environment variable is not set")

    ref = ref.resolve()

    return _format_statblock(
        monster_model=MonsterModel.from_monster(
            stats=stats,
            template=ref.template,
            variant=ref.variant,  # type: ignore
            monster=ref.monster,  # type: ignore
            species=ref.species,
            base_url=base_url,
        ),
        stats=stats,
        rng=rng,
        output=output,
    )


@router.post("/generate")
def generate_statblock_from_request(
    request: StatblockGenerationRequest = Body(...),
    output: Annotated[
        StatblockFormat | None,
        Query(title="return format", examples=StatblockFormat.All()),
    ] = None,
):
    rng = np.random.default_rng()

    settings_args = dict()
    if request.hp_multiplier is not None:
        settings_args["hp_multiplier"] = request.hp_multiplier
    if request.damage_multiplier is not None:
        settings_args["damage_multiplier"] = request.damage_multiplier
    if request.powers is not None:
        settings_args["power_weights"] = {p: 1.0 for p in request.powers}

    ref, stats = generate_monster(
        template_or_variant_key=request.monster_key,
        ref_resolver=ref_resolver,
        rng=rng,
        **settings_args,
    )

    if stats is None or ref is None:
        raise HTTPException(
            status_code=404, detail=f"Monster not found: {request.monster_key}"
        )
    base_url = os.environ.get("SITE_URL")
    if base_url is None:
        raise ValueError("SITE_URL environment variable is not set")

    ref = ref.resolve()

    return _format_statblock(
        monster_model=MonsterModel.from_monster(
            stats=stats,
            template=ref.template,
            variant=ref.variant,  # type: ignore
            monster=ref.monster,  # type: ignore
            species=ref.species,
            base_url=base_url,
        ),
        stats=stats,
        rng=rng,
        output=output,
    )


def _format_statblock(
    monster_model: MonsterModel,
    stats: Statblock,
    rng: np.random.Generator,
    output: Annotated[
        StatblockFormat | None,
        Query(title="return format", examples=StatblockFormat.All()),
    ] = None,
) -> Response:
    if output is None:
        output = StatblockFormat.html

    statblock_html = monster_model.statblock_html
    lore_html = monster_model.template_html

    if len(monster_model.images) == 0:
        img_src = None
        image_html = None
    else:
        image_index = rng.choice(len(monster_model.images))
        img_src = monster_model.images[image_index]
        image_html = f'<img class="masked monster-image" src="{img_src}" alt="{monster_model.name} image" />'

    loadouts = [asdict(lo) for lo in monster_model.loadouts]

    if output == StatblockFormat.html:
        html = f'<div class="statblock-container">{statblock_html}\n{lore_html or ""}\n{image_html or ""}</div>'
        return HTMLResponse(content=html)
    elif output == StatblockFormat.monster_only:
        return HTMLResponse(content=statblock_html)
    elif output == StatblockFormat.json:
        json_data = dict(
            monster_meta=MonsterMeta(
                monster_key=monster_model.key,
                template_key=monster_model.template_key,
            ).model_dump(mode="json"),
            statblock_html=statblock_html,
            lore_html=lore_html,
            image=img_src,
            loadouts=loadouts,
        )
        return JSONResponse(content=json_data)
    elif output == StatblockFormat.md_5esrd:
        markdown = render_statblock_markdown(stats, "5esrd")
        return Response(content=markdown, media_type="text/markdown")
    elif output == StatblockFormat.md_gmbinder:
        markdown = render_statblock_markdown(stats, "gmbinder")
        return Response(content=markdown, media_type="text/markdown")
    elif output == StatblockFormat.md_homebrewery:
        markdown = render_statblock_markdown(stats, "homebrewery")
        return Response(content=markdown, media_type="text/markdown")
    elif output == StatblockFormat.md_blackflag:
        markdown = render_statblock_markdown(stats, "blackflag")
        return Response(content=markdown, media_type="text/markdown")
    else:
        raise ValueError(f"Unsupported output format: {output}")

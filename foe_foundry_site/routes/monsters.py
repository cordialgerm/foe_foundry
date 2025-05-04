from __future__ import annotations

import os
from typing import Annotated

import numpy as np
from backports.strenum import StrEnum
from fastapi import APIRouter, Query, Response
from fastapi.responses import HTMLResponse, JSONResponse

from foe_foundry.creatures import random_template_and_settings
from foe_foundry_data.monsters import MonsterModel

router = APIRouter(prefix="/api/v1/monsters")


class MonsterFormat(StrEnum):
    html = "html"
    monster_only = "monster_only"
    json = "json"

    @staticmethod
    def All():
        return [MonsterFormat.html, MonsterFormat.monster_only, MonsterFormat.json]


@router.get("/random")
def random_monster(
    output: Annotated[
        MonsterFormat | None, Query(title="return format", examples=MonsterFormat.All())
    ] = None,
) -> Response:
    rng = np.random.default_rng()
    template, settings = random_template_and_settings(
        rng=rng,
        filter_templates=None,
        filter_variants=None,
        filter_suggested_crs=None,
        species_filter=None,
    )

    stats = template.generate(settings).finalize()

    if output is None:
        output = MonsterFormat.html

    base_url = os.environ.get("SITE_URL")
    if base_url is None:
        raise ValueError("SITE_URL environment variable is not set")
    monster_model = MonsterModel.from_monster(
        stats=stats, template=template, base_url=base_url
    )

    statblock_html = monster_model.statblock_html
    lore_html = monster_model.template_html

    if len(monster_model.images) == 0:
        img_src = None
        image_html = None
    else:
        image_index = rng.choice(len(monster_model.images))
        img_src = monster_model.images[image_index]
        image_html = f'<img class="masked monster-image" src="{img_src}" alt="{monster_model.name} image" />'

    if output == MonsterFormat.html:
        html = f'<div class="statblock-container">{statblock_html}\n{lore_html or ""}\n{image_html or ""}</div>'
        return HTMLResponse(content=html)
    elif output == MonsterFormat.monster_only:
        return HTMLResponse(content=statblock_html)
    else:
        json_data = dict(
            statblock_html=statblock_html, lore_html=lore_html, image=img_src
        )
        return JSONResponse(content=json_data)

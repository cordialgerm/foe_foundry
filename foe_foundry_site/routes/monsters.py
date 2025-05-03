from __future__ import annotations

import os
from pathlib import Path
from typing import Annotated

import numpy as np
from backports.strenum import StrEnum
from fastapi import APIRouter, Query, Response

from foe_foundry.creatures import random_template_and_settings
from foe_foundry.jinja import render_statblock_fragment
from foe_foundry.markdown import markdown

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

    lore_md = template.lore_md
    images = template.get_images(settings.variant.key)
    if len(images):
        image_index = rng.choice(len(images))
        image = images[image_index]
        rel_path = image.relative_to(Path.cwd() / "docs").as_posix()
        img_src = os.environ.get("BASE_URL", "") + rel_path
    else:
        img_src = None

    statblock_html = render_statblock_fragment(stats)
    lore_html = markdown(lore_md).html
    image_html = (
        (f'<img class="monster-image masked" src="{img_src}" alt="{stats.name}" />')
        if img_src
        else ""
    )

    if output == MonsterFormat.html:
        html = f'<div class="statblock-container">{statblock_html}\n{lore_html}\n{image_html}</div>'
        return Response(content=html, media_type="text/html")
    elif output == MonsterFormat.monster_only:
        return Response(content=statblock_html, media_type="text/html")
    else:
        json_data = dict(
            statblock_html=statblock_html, lore_html=lore_html, image=img_src
        )
        return Response(content=json_data, media_type="application/json")

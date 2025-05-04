from __future__ import annotations

import os
from typing import Annotated

import numpy as np
from backports.strenum import StrEnum
from fastapi import APIRouter, HTTPException, Query, Response
from fastapi.responses import HTMLResponse, JSONResponse

from foe_foundry.creatures import (
    CreatureVariant,
    SuggestedCr,
    random_template_and_settings,
)
from foe_foundry.markdown import MonsterRefResolver
from foe_foundry_data.monsters import MonsterModel

router = APIRouter(prefix="/api/v1/monsters")
ref_resolver = MonsterRefResolver()


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
    return _format_monster(monster_model=monster_model, rng=rng, output=output)


@router.get("/{template_or_variant_key}")
def get_monster(
    template_or_variant_key: str,
    output: Annotated[
        MonsterFormat | None, Query(title="return format", examples=MonsterFormat.All())
    ] = None,
):
    rng = np.random.default_rng()
    ref = ref_resolver.resolve_monster_ref(template_or_variant_key)
    if ref is None:
        raise HTTPException(status_code=404, detail="Monster not found")

    if ref.suggested_cr is None:
        options = []
        for variant in ref.template.variants:
            for suggested_cr in variant.suggested_crs:
                options.append((variant, suggested_cr))

        index = rng.choice(len(options))
        variant, suggested_cr = options[index]
        ref = ref.copy(variant=variant, suggested_cr=suggested_cr)

    # we know these values aren't None because we checked above
    template = ref.template
    variant: CreatureVariant = ref.variant  # type: ignore
    suggested_cr: SuggestedCr = ref.suggested_cr  # type: ignore

    stats = template.generate_suggested_cr(
        variant=variant, suggested_cr=suggested_cr, rng=rng
    ).finalize()
    base_url = os.environ.get("SITE_URL")
    if base_url is None:
        raise ValueError("SITE_URL environment variable is not set")

    return _format_monster(
        monster_model=MonsterModel.from_monster(
            stats=stats, template=template, base_url=base_url
        ),
        rng=rng,
        output=output,
    )


def _format_monster(
    monster_model: MonsterModel,
    rng: np.random.Generator,
    output: Annotated[
        MonsterFormat | None, Query(title="return format", examples=MonsterFormat.All())
    ] = None,
) -> Response:
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

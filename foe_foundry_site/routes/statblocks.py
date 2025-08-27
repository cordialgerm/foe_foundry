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
from foe_foundry_data.generate import generate_monster
from foe_foundry_data.monsters import MonsterModel
from foe_foundry_data.refs import MonsterRefResolver

from ..auth.dependencies import AuthContextDep, require_credits, SessionDep
from .data import MonsterMeta

router = APIRouter(prefix="/api/v1/statblocks")
ref_resolver = MonsterRefResolver()


class StatblockFormat(StrEnum):
    html = "html"
    monster_only = "monster_only"
    json = "json"

    @staticmethod
    def All():
        return [
            StatblockFormat.html,
            StatblockFormat.monster_only,
            StatblockFormat.json,
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
    auth_context: AuthContextDep = None,
    session: SessionDep = None,
) -> Response:
    # Check and use credits
    if not auth_context.can_use_credits(1):
        if auth_context.is_anonymous:
            raise HTTPException(
                status_code=402, 
                detail=f"Anonymous credit limit reached ({auth_context.anon_session.get_credit_limit()} generations). Create an account to continue."
            )
        else:
            raise HTTPException(
                status_code=402,
                detail=f"Insufficient credits. You have {auth_context.get_credits_remaining()} credits remaining."
            )
    
    # Use credit
    auth_context.use_credits(1)
    
    # Update database
    if auth_context.user:
        session.add(auth_context.user)
        session.commit()
    elif auth_context.anon_session:
        session.add(auth_context.anon_session)
        session.commit()
    
    # Generate the statblock
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
    return _format_statblock(monster_model=monster_model, rng=rng, output=output)


@router.get("/{template_or_variant_key}")
def get_statblock(
    template_or_variant_key: str,
    output: Annotated[
        StatblockFormat | None,
        Query(title="return format", examples=StatblockFormat.All()),
    ] = None,
    auth_context: AuthContextDep = None,
    session: SessionDep = None,
):
    # Check and use credits
    if not auth_context.can_use_credits(1):
        if auth_context.is_anonymous:
            raise HTTPException(
                status_code=402, 
                detail=f"Anonymous credit limit reached ({auth_context.anon_session.get_credit_limit()} generations). Create an account to continue."
            )
        else:
            raise HTTPException(
                status_code=402,
                detail=f"Insufficient credits. You have {auth_context.get_credits_remaining()} credits remaining."
            )
    
    # Use credit
    auth_context.use_credits(1)
    
    # Update database
    if auth_context.user:
        session.add(auth_context.user)
        session.commit()
    elif auth_context.anon_session:
        session.add(auth_context.anon_session)
        session.commit()
    
    # Generate the statblock
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
    auth_context: AuthContextDep = None,
    session: SessionDep = None,
):
    # Check and use credits
    if not auth_context.can_use_credits(1):
        if auth_context.is_anonymous:
            raise HTTPException(
                status_code=402, 
                detail=f"Anonymous credit limit reached ({auth_context.anon_session.get_credit_limit()} generations). Create an account to continue."
            )
        else:
            raise HTTPException(
                status_code=402,
                detail=f"Insufficient credits. You have {auth_context.get_credits_remaining()} credits remaining."
            )
    
    # Use credit
    auth_context.use_credits(1)
    
    # Update database
    if auth_context.user:
        session.add(auth_context.user)
        session.commit()
    elif auth_context.anon_session:
        session.add(auth_context.anon_session)
        session.commit()
    
    # Generate the statblock
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
        rng=rng,
        output=output,
    )


def _format_statblock(
    monster_model: MonsterModel,
    rng: np.random.Generator,
    output: Annotated[
        StatblockFormat | None,
        Query(title="return format", examples=StatblockFormat.All()),
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

    loadouts = [asdict(lo) for lo in monster_model.loadouts]

    if output == StatblockFormat.html:
        html = f'<div class="statblock-container">{statblock_html}\n{lore_html or ""}\n{image_html or ""}</div>'
        return HTMLResponse(content=html)
    elif output == StatblockFormat.monster_only:
        return HTMLResponse(content=statblock_html)
    else:
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

from __future__ import annotations

from enum import auto

import numpy as np
from backports.strenum import StrEnum
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware

from foe_foundry import (
    AllCreatureTemplates,
    AllRoles,
    Statblock,
    general_use_stats,
    get_common_stats,
    get_creature_template,
    get_role,
)
from foe_foundry.templates import render_html_fragment, render_html_inline

from .stats import StatblockModel

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:3000",
    "http://localhost:3001",
    "https://cordialgerm87.pythonanywhere.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

rng = np.random.default_rng(20210518)


def rng_factory() -> np.random.Generator:
    return rng


def _random_stats(
    creature: str | None = None, role: str | None = None, cr: str | int | float | None = None
) -> Statblock:
    rng = rng_factory()

    if not creature:
        creature_index = rng.choice(len(AllCreatureTemplates))
        creature = AllCreatureTemplates[creature_index].name

    if not role:
        role_index = rng.choice(len(AllRoles))
        role = AllRoles[role_index].name

    if cr is None:
        cr_index = rng.choice(len(general_use_stats.All))
        cr = general_use_stats.All[cr_index].name

    creature_template = get_creature_template(creature)
    role_template = get_role(role)
    base_stats = get_common_stats(cr)
    stats = creature_template.create(
        base_stats=base_stats,
        role_template=role_template,
        rng_factory=rng_factory,
    )
    return stats


def _render_stats(render: RenderMode, **args) -> Response:
    stats = _random_stats(**args)

    if render == RenderMode.full:
        html = render_html_inline(stats)
    elif render == RenderMode.partial:
        html = render_html_fragment(stats)
    else:
        raise ValueError(f"Unsupported render '{render}'")
    return Response(content=html, media_type="text/html")


@app.get("/")
def get_root():
    return _render_stats(render=RenderMode.full)


class RenderMode(StrEnum):
    full = auto()
    partial = auto()


@app.get("/statblocks/random/{creature}/{role}/{cr}")
def view_random_stats3(
    creature: str, role: str, cr: str | int | float, render: RenderMode | None = None
) -> Response:
    return _render_stats(creature=creature, role=role, cr=cr, render=render or RenderMode.full)


@app.get("/statblocks/random/{creature}/{role}")
def view_random_stats2(creature: str, role: str, render: RenderMode | None = None) -> Response:
    return _render_stats(
        creature=creature, role=role, cr=None, render=render or RenderMode.full
    )


@app.get("/statblocks/random/{creature}")
def view_random_stats1(creature: str, render: RenderMode | None = None) -> Response:
    return _render_stats(
        creature=creature, role=None, cr=None, render=render or RenderMode.full
    )


@app.get("/api/v1/statblocks/random/{creature}/{role}/{cr}")
def get_random_stats(creature: str, role: str, cr: str | int | float) -> StatblockModel:
    stats = _random_stats(creature, role, cr)
    return StatblockModel.from_args(stats.__copy_args__())

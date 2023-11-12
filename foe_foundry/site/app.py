from __future__ import annotations

import numpy as np
from fastapi import FastAPI, Response

from foe_foundry import (
    AllCreatureTemplates,
    AllRoles,
    Statblock,
    general_use_stats,
    get_common_stats,
    get_creature_template,
    get_role,
)
from foe_foundry.templates import render_html_inline

from .stats import StatblockModel

app = FastAPI()

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


def _render_stats(**args) -> Response:
    stats = _random_stats(**args)
    html = render_html_inline(stats)
    return Response(content=html, media_type="text/html")


@app.get("/")
def get_root():
    return _render_stats()


@app.get("/statblocks/random/{creature}/{role}/{cr}")
def view_random_stats(creature: str, role: str, cr: str | int | float) -> Response:
    return _render_stats(creature=creature, role=role, cr=cr)


@app.get("/api/v1/statblocks/random/{creature}/{role}/{cr}")
def get_random_stats(creature: str, role: str, cr: str | int | float) -> StatblockModel:
    stats = _random_stats(creature, role, cr)
    return StatblockModel.from_args(stats.__copy_args__())

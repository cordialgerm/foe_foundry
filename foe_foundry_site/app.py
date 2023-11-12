import numpy as np
from fastapi import FastAPI, Response

from foe_foundry import Statblock, get_common_stats, get_creature_template, get_role
from foe_foundry.templates import render_html_inline
from foe_foundry.utils.rng import RngFactory

from .stats import StatblockModel

app = FastAPI()

rng = np.random.default_rng(20210518)


def rng_factory() -> np.random.Generator:
    return rng


def _random_stats(creature: str, role: str, cr: str | int | float) -> Statblock:
    creature_template = get_creature_template(creature)
    role_template = get_role(role)
    base_stats = get_common_stats(cr)
    stats = creature_template.create(
        base_stats=base_stats,
        role_template=role_template,
        rng_factory=rng_factory,
    )
    return stats


@app.get("/")
def get_root():
    return {"Hello": "World"}


@app.get("/statblocks/random/{creature}/{role}/{cr}")
def view_random_stats(creature: str, role: str, cr: str | int | float) -> Response:
    stats = _random_stats(creature, role, cr)
    html = render_html_inline(stats)
    return Response(content=html, media_type="text/html")


@app.get("/api/v1/statblocks/random/{creature}/{role}/{cr}")
def get_random_stats(creature: str, role: str, cr: str | int | float) -> StatblockModel:
    stats = _random_stats(creature, role, cr)
    return StatblockModel.from_args(stats.__copy_args__())

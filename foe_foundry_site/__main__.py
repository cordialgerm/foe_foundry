import os

import uvicorn
from fastapi import FastAPI, Response

from foe_foundry import Statblock, get_common_stats, get_creature_template, get_role
from foe_foundry.templates import render_html_inline

from .stats import StatblockModel

app = FastAPI()


def _random_stats(creature: str, role: str, cr: str | int | float) -> Statblock:
    creature_template = get_creature_template(creature)
    role_template = get_role(role)
    base_stats = get_common_stats(cr)
    rng_seed = 20210518
    stats = creature_template.create(
        base_stats=base_stats, rng_seed=rng_seed, role_template=role_template
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


if __name__ == "__main__":
    uvicorn.run(app, port=int(os.getenv("PORT", 8080)), proxy_headers=True)

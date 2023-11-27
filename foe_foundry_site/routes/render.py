from enum import auto

import numpy as np
from backports.strenum import StrEnum
from fastapi import Response

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

rng = np.random.default_rng(20210518)


class RenderMode(StrEnum):
    full = auto()
    partial = auto()


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

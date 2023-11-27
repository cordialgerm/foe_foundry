from __future__ import annotations

from fastapi import APIRouter, Response

from ..data import StatblockModel
from .render import RenderMode, _random_stats, _render_stats

router = APIRouter()


@router.get("/statblocks/random/{creature}/{role}/{cr}")
def view_random_stats3(
    creature: str, role: str, cr: str | int | float, render: RenderMode | None = None
) -> Response:
    return _render_stats(creature=creature, role=role, cr=cr, render=render or RenderMode.full)


@router.get("/statblocks/random/{creature}/{role}")
def view_random_stats2(creature: str, role: str, render: RenderMode | None = None) -> Response:
    return _render_stats(
        creature=creature, role=role, cr=None, render=render or RenderMode.full
    )


@router.get("/statblocks/random/{creature}")
def view_random_stats1(creature: str, render: RenderMode | None = None) -> Response:
    return _render_stats(
        creature=creature, role=None, cr=None, render=render or RenderMode.full
    )


@router.get("/api/v1/statblocks/random/{creature}/{role}/{cr}")
def get_random_stats(creature: str, role: str, cr: str | int | float) -> StatblockModel:
    stats = _random_stats(creature, role, cr)
    return StatblockModel.from_args(stats.__copy_args__())

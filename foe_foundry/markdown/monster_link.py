import numpy as np
from markupsafe import Markup

from foe_foundry.creatures import (
    GenerationSettings,
)
from foe_foundry.jinja import render_statblock_fragment

from .monster_ref import MonsterRef


def _link(ref: MonsterRef, url: str) -> Markup | None:
    if ref.suggested_cr is not None:
        return Markup(
            f"<a href='{url}' class='monster-link' data-monster-template='{ref.template.key}' data-monster='{ref.suggested_cr.key}'><strong>{ref.original_monster_name}</strong></a>"
        )
    else:
        return Markup(
            f"<a href='{url}' class='monster-link' data-monster-template='{ref.template.key}'><strong>{ref.original_monster_name}</strong></a>"
        )


def monster_link(ref: MonsterRef, base_url: str) -> Markup | None:
    """Generates a link to the monster template or variant."""

    if base_url.endswith("/"):
        base_url = base_url[:-1]

    if ref is None:
        return None
    elif ref.suggested_cr is not None:
        href = f"{base_url}/monsters/{ref.template.key}#{ref.suggested_cr.key}"
        return _link(ref, href)
    else:
        href = f"https://foefoundry.com/monsters/{ref.template.key}"
        return _link(ref, href)


def monster_button(ref: MonsterRef, base_url: str) -> Markup | None:
    """Generates a button to summon the monster template or variant."""

    if base_url.endswith("/"):
        base_url = base_url[:-1]

    if ref is None:
        return None
    else:
        url = f"{base_url}/generate/?template={ref.template.key}"
        if ref.suggested_cr is not None:
            url += f"&variant={ref.suggested_cr.key}"

        monster = _link(ref, url)

    return Markup(
        f"<div class='statblock-ref-button burnt-parchment burnt-parchment-button branding'>Summon your own {monster}</div>"
    )


def monster_statblock(ref: MonsterRef) -> Markup | None:
    if ref is None:
        return None

    def rng_factory():
        return np.random.default_rng()

    template = ref.template
    variant = ref.variant if ref.variant is not None else template.variants[0]
    suggested_cr = (
        ref.suggested_cr if ref.suggested_cr is not None else variant.suggested_crs[0]
    )

    stats = template.generate(
        GenerationSettings(
            creature_name=suggested_cr.name,
            creature_template=template.name,
            variant=variant,
            cr=suggested_cr.cr,
            species=None,
            is_legendary=suggested_cr.is_legendary,
            rng=rng_factory(),
        )
    ).finalize()
    html = render_statblock_fragment(stats)
    return Markup(html)

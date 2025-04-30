import numpy as np
from markupsafe import Markup

from foe_foundry.creatures import (
    GenerationSettings,
)
from foe_foundry.jinja import render_statblock_fragment

from .monster_ref import MonsterRef


def monster_link(ref: MonsterRef) -> Markup | None:
    """Generates a link to the monster template or variant."""
    if ref is None:
        return None
    elif ref.suggested_cr is not None:
        href = (
            f"https://foefoundry.com/monsters/{ref.template.key}#{ref.suggested_cr.key}"
        )
        return Markup(
            f"<a href='{href}' class='monster-link' data-monster-template='{ref.template.key}' data-monster='{ref.suggested_cr.key}'><strong>{ref.original_monster_name}</strong></a>"
        )
    else:
        href = f"https://foefoundry.com/monsters/{ref.template.key}"
        return Markup(
            f"<a href='{href}' class='monster-link' data-monster-template='{ref.template.key}'><strong>{ref.original_monster_name}</strong></a>"
        )


def monster_button(ref: MonsterRef) -> Markup | None:
    """Generates a button to summon the monster template or variant."""
    if ref is None:
        return None
    else:
        monster = monster_link(ref)

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

import numpy as np
from markupsafe import Markup

from foe_foundry.creatures import (
    GenerationSettings,
)

from ..jinja import render_statblock_fragment
from ..refs import MonsterRef


def _link(ref: MonsterRef, url: str) -> Markup | None:
    if ref.monster is not None:
        return Markup(
            f"<a href='{url}' class='monster-link' data-monster='{ref.monster.key}'><strong>{ref.original_monster_name}</strong></a>"
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
    elif ref.monster is not None:
        href = f"{base_url}/monsters/{ref.template.key}/#{ref.monster.key}"
        return _link(ref, href)
    else:
        href = f"https://foefoundry.com/monsters/{ref.template.key}/"
        return _link(ref, href)


def monster_button(ref: MonsterRef, base_url: str) -> Markup | None:
    """Generates a button to summon the monster template or variant."""

    if base_url.endswith("/"):
        base_url = base_url[:-1]

    if ref is None:
        return None
    else:
        url = f"{base_url}/generate/?template={ref.template.key}"
        if ref.monster is not None:
            url += f"&variant={ref.monster.key}"

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
    monster = ref.monster if ref.monster is not None else variant.monsters[0]

    if ref.args is None:
        power_weights = {}
    else:
        power_weights = ref.args.get("power_weights", {})

    stats = template.generate(
        GenerationSettings(
            creature_name=monster.name,
            monster_template=template.name,
            monster_key=monster.key,
            variant=variant,
            monster=monster,
            cr=monster.cr,
            species=ref.species,
            is_legendary=monster.is_legendary,
            rng=rng_factory(),
            power_weights=power_weights,
        )
    ).finalize()
    html = render_statblock_fragment(stats)
    return Markup(html)

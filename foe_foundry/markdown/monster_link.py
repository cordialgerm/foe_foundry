from markupsafe import Markup

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

    brand = '<span class="branding"><img src="img/favicon.png" alt="Foe Foundry Skull Icon"></span>'
    return Markup(
        f"<div class='statblock-ref-button burnt-parchment burnt-parchment-button'>Summon your own {monster}{brand}</div>"
    )

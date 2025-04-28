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

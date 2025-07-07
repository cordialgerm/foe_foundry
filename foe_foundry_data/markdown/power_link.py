from markupsafe import Markup

from foe_foundry.powers import Power

from ..icons import inline_icon


def power_link(power: Power, base_url: str) -> Markup | None:
    """Generates a link to the power."""

    if base_url.endswith("/"):
        base_url = base_url[:-1]

    if power is None:
        return None

    href = f"{base_url}/powers/{power.theme.lower()}/#{power.key}"

    icon = inline_icon(power.icon) if power.icon else None
    if icon is None:
        icon = ""
    else:
        return Markup(
            f"<a href='{href}' class='power-link' data-power='{power.key}'>{icon}<strong>{power.name}</strong></a>"
        )

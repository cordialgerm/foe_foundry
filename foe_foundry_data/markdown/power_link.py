from markupsafe import Markup

from foe_foundry.powers import Power


def power_link(power: Power, base_url: str) -> Markup | None:
    """Generates a link to the power."""

    if base_url.endswith("/"):
        base_url = base_url[:-1]

    if power is None:
        return None

    href = f"{base_url}/powers/{power.theme.lower()}#{power.key}"
    return Markup(
        f"<a href='{href}' class='power-link' data-power='{power.key}'><strong>{power.name}</strong></a>"
    )

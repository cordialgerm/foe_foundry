from .env import JinjaEnv


def render_power_fragment(power) -> str:
    """Renders a power HTML fragment for a single power"""

    template = JinjaEnv.get_template("power.html.j2")
    context = dict(power=power)
    html_raw = template.render(context)
    return html_raw

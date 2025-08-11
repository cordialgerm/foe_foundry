from foe_foundry.statblocks import Statblock

from .data import StatblockJinjaContext
from .env import JinjaEnv


def render_statblock_fragment(stats: Statblock) -> str:
    """Renders a statblock HTML fragment for a single statblock"""

    template = JinjaEnv.get_template("statblock.html.j2")
    data = StatblockJinjaContext.from_statblock(stats)
    context = dict(statblock=data.to_dict())
    html_raw = template.render(context)
    return html_raw

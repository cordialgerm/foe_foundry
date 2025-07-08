from typing import TYPE_CHECKING

from foe_foundry.features import ActionType

from ..icons import inline_icon
from .env import JinjaEnv

if TYPE_CHECKING:
    from ..powers import PowerModel


def render_power_fragment(power: "PowerModel", header_tag: str = "h2") -> str:
    """Renders a power HTML fragment for a single power"""

    template = JinjaEnv.get_template("power.html.j2")

    passives = [f for f in power.features if f.action == ActionType.Feature.name]
    actions = [f for f in power.features if f.action == ActionType.Action.name]
    bonus_actions = [
        f for f in power.features if f.action == ActionType.BonusAction.name
    ]
    reactions = [f for f in power.features if f.action == ActionType.Reaction.name]

    spellcasting = [f for f in power.features if f.is_spellcasting]
    attack = [f for f in power.features if f.is_attack]

    if power.icon is not None:
        icon = inline_icon(power.icon)
    else:
        icon = None

    context = dict(
        power=power,
        header_tag=header_tag,
        icon=icon,
        passives=passives,
        actions=actions,
        bonuses=bonus_actions,
        reactions=reactions,
        attacks=attack,
        spellcasting=spellcasting,
        reaction_header=power.reaction_header,
        monsters=power.monsters,
    )
    html_raw = template.render(context)
    return html_raw

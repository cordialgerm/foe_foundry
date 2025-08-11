from typing import TYPE_CHECKING

from foe_foundry.features import ActionType

from ..icons import inline_icon
from .env import JinjaEnv

if TYPE_CHECKING:
    from ..powers import PowerModel


def render_power_fragment(power: "PowerModel", header_tag: str = "h2") -> str:
    """Renders a power HTML fragment for a single power"""

    template = JinjaEnv.get_template("power.html.j2")

    passives = [
        f
        for f in power.features
        if f.action == ActionType.Feature.name
        and not f.is_spellcasting
        and not f.is_attack
    ]
    actions = [
        f
        for f in power.features
        if f.action == ActionType.Action.name
        and not f.is_spellcasting
        and not f.is_attack
    ]
    bonus_actions = [
        f
        for f in power.features
        if f.action == ActionType.BonusAction.name
        and not f.is_spellcasting
        and not f.is_attack
    ]
    reactions = [
        f
        for f in power.features
        if f.action == ActionType.Reaction.name
        and not f.is_spellcasting
        and not f.is_attack
    ]

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
        monsters_html=power.used_by_monsters_html,
    )
    html_raw = template.render(context)
    return html_raw

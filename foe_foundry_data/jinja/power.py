from foe_foundry.features import ActionType

from ..powers import PowerModel
from .env import JinjaEnv


def render_power_fragment(power: PowerModel) -> str:
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

    context = dict(
        power=power,
        passives=passives,
        actions=actions,
        bonuses=bonus_actions,
        reactions=reactions,
        attacks=attack,
        spellcasting=spellcasting,
    )
    html_raw = template.render(context)
    return html_raw

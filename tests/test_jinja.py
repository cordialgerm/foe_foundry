from bs4 import BeautifulSoup

from foe_foundry.powers.creature_type import celestial, demon
from foe_foundry.powers.roles import ambusher
from foe_foundry.powers.spellcaster import necromancer
from foe_foundry.powers.themed import bestial, breath, tough
from foe_foundry_data.jinja import render_power_fragment
from foe_foundry_data.powers import PowerModel


def _check_header(html: str, header: str):
    """Check if the HTML contains the header"""
    bs = BeautifulSoup(html, "html.parser")

    def is_header(tag):
        return tag.name == "h4" and tag.text == header

    bs_header = bs.find(is_header)

    assert bs_header is not None, "Header not found"
    assert bs_header.text == header, (
        f"Header text does not match: {bs_header.text} != {header}"
    )


def test_bonus_action_rendering():
    power = PowerModel.from_power(ambusher.CunningAction)
    fragment = render_power_fragment(power)
    _check_header(fragment, "Bonus Actions")


def test_trait_rendering():
    power = PowerModel.from_power(tough.MagicResistance)
    fragment = render_power_fragment(power)
    _check_header(fragment, "Traits")


def test_reaction_rendering():
    power = PowerModel.from_power(bestial.RetributiveStrike)
    fragment = render_power_fragment(power)
    _check_header(fragment, "Reactions")


def test_action_rendering():
    power = PowerModel.from_power(breath.AcidBreath)
    fragment = render_power_fragment(power)
    _check_header(fragment, "Actions")


def test_spellcasting_rendering():
    power = PowerModel.from_power(necromancer.NecromancerAdept)
    fragment = render_power_fragment(power)
    _check_header(fragment, "Spellcasting")


def test_attack_rendering():
    power = PowerModel.from_power(demon.DemonicBite)
    fragment = render_power_fragment(power)
    _check_header(fragment, "Attacks")


def test_divine_law_multiple_columns():
    power = PowerModel.from_power(celestial.DivineLaw)
    assert power.columns_suggested

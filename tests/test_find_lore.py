from foe_foundry.creatures.mage.mage import MageTemplate
from foe_foundry.creatures.vrock.vrock import VrockTemplate


def test_template_lore_md():
    assert MageTemplate.lore_md != ""
    assert VrockTemplate.lore_md is None

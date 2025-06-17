from foe_foundry.utils.image import has_transparent_edges


def test_has_transparent_edges():
    assert has_transparent_edges("docs/img/monsters/druid.webp")
    assert has_transparent_edges("docs/img/monsters/ogre.webp")
    assert not has_transparent_edges("docs/img/monsters/owlbear.webp")

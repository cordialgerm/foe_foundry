from foe_foundry.utils.image import has_transparent_edges, is_grayscaleish


def test_has_transparent_edges():
    assert has_transparent_edges("docs/img/monsters/druid.webp")
    assert has_transparent_edges("docs/img/monsters/ogre.webp")
    assert not has_transparent_edges("docs/img/monsters/owlbear.webp")


def test_is_grayscaleish():
    assert is_grayscaleish("docs/img/blogs/trap.webp")
    assert not is_grayscaleish("docs/img/monsters/darklord.webp")

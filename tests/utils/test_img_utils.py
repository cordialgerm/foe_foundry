from foe_foundry.utils.image import (
    get_dominant_edge_color,
    has_transparent_edges,
    is_grayscaleish,
)


def test_has_transparent_edges():
    assert has_transparent_edges("docs/img/monsters/druid.webp")
    assert has_transparent_edges("docs/img/monsters/ogre.webp")
    assert not has_transparent_edges("docs/img/monsters/owlbear.webp")


def test_is_grayscaleish():
    assert is_grayscaleish("docs/img/blogs/trap.webp")
    assert not is_grayscaleish("docs/img/monsters/darklord.webp")


def test_get_edge_color():
    assert get_dominant_edge_color("docs/img/monsters/simulacrum.webp") == "#c2c2c2"
    assert get_dominant_edge_color("docs/img/monsters/ogre.webp") is None

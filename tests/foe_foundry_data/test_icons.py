from pathlib import Path

from foe_foundry_data.icons import icon_path, inline_icon, og_image_for_icon


def test_icon_path():
    assert icon_path("favicon") is not None
    assert icon_path("evil-favicon") is None


def test_inline_icon():
    icon_markup = inline_icon("favicon")
    assert icon_markup is not None
    assert '<span class="inline-icon"' in str(icon_markup)

    # Test with fill color
    icon_markup_with_fill = inline_icon("favicon", fill="#ff0000")
    assert 'fill="#ff0000"' in str(icon_markup_with_fill)


def test_og_image_for_icon():
    output_dir = Path(__file__).parent.parent / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "og_favicon_test.png"

    result = og_image_for_icon(
        icon="favicon", title="Reckless Powers", output_path=output_path
    )
    assert result == output_path
    assert result.exists()

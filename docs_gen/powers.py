from pathlib import Path

import mkdocs_gen_files

from foe_foundry.utils import slug_to_title
from foe_foundry_data.icons import inline_icon, og_image_for_icon
from foe_foundry_data.powers import PowerCategory, PowerModel, Powers

from .types import FilesToGenerate


def generate_all_powers_content() -> FilesToGenerate:
    """Generate all powers content without writing to mkdocs_gen_files.

    Returns FilesToGenerate with all the files to be written.
    """
    files = {}

    # Create the main index content
    lines = [
        "---",
        "title: All Powers | Foe Foundry",
        "description: Browse 600+ handcrafted monster powers for tabletop RPGs. Find unique abilities and build the perfect monster for your encounters.",
        "image: img/icons/favicon.webp",
        "hide:",
        "   - backlinks",
        "---",
        "# All Monster Powers\n",
        "Monster Powers are the beating heart of Foe Foundry. Powers are flavorful, handcrafted abilities that make every 5E monster feel unique, dangerous, and ready for the table. Whether it's a venomous strike, a cursed aura, or a spell-laced scream, each Power is designed to challenge players and inspire GMs. Powers are organized by theme to help you discover exactly the right vibe for your next encounter, and they scale cleanly with CR so you can drop them into any campaign.  \n",
        "Foe Foundry automatically selects relevant powers for you basedd on the creature template that you're using, but you can also add or remove powers directly in the generator.  \n",
        f"Browse all {len(Powers.PowerLookup)} monster powers by theme below:\n",
    ]

    for power_category in PowerCategory.All():
        powers_by_theme = {
            t: [p for p in ps if p.power_category.lower() == power_category.lower()]
            for t, ps in Powers.PowersByTheme.items()
        }
        n = sum(len(p) for t, p in powers_by_theme.items())
        lines.append(f"## {slug_to_title(power_category)} Powers ({n})\n")

        lines.append("<div class='list-with-columns'></div>\n")
        for theme, powers in powers_by_theme.items():
            if len(powers) == 0:
                continue

            lines.append(
                f"- [{slug_to_title(theme)} Powers ({len(powers)})]({theme}.md)\n"
            )

    # Add main index file
    files["powers/all.md"] = "\n".join(lines)

    # Generate theme files
    for theme, powers in Powers.PowersByTheme.items():
        theme_content = generate_theme_file_content(theme, powers)
        files[f"powers/{theme}.md"] = theme_content

    return FilesToGenerate(name="powers", files=files)


def generate_all_powers():
    """Generate all powers and write directly to mkdocs_gen_files."""
    result = generate_all_powers_content()

    # Write all files into the virtual MkDocs build
    for filename, content in result.files.items():
        with mkdocs_gen_files.open(filename, "w") as f:
            f.write(content)


def generate_theme_file_content(theme: str, powers: list[PowerModel]) -> str:
    """Generate content for a theme file without writing to mkdocs_gen_files."""
    # Sum monster_count by icon and pick the icon with the highest monster_count
    icon_counts = {}
    for p in powers:
        if p.icon:
            icon_counts[p.icon] = icon_counts.get(p.icon, 0) + 10 + len(p.monsters)
    if icon_counts:
        icon = max(icon_counts, key=icon_counts.get)  # type: ignore
    else:
        icon = "favicon"

    theme_title = slug_to_title(theme)
    theme_description = theme_title.lower()

    icon_html = inline_icon(icon)

    og_image_dir = Path.cwd() / "site" / "img" / "og"
    og_image_dir.mkdir(parents=True, exist_ok=True)
    og_image_path = og_image_dir / f"{theme}-og-image.png"
    og_image_path_rel = og_image_path.relative_to(Path.cwd() / "site")
    og_image_for_icon(
        icon=icon, title=theme_title + " Powers", output_path=og_image_path
    )

    lines = [
        "---",
        f"title: {theme_title} Powers | Foe Foundry",
        f"description: Discover {len(powers)} {theme_description}-themed free powers for your next 5E monster.\n",
        f"image: {og_image_path_rel}",
        "---\n",
        f"# {icon_html} {theme_title} Powers ({len(powers)})\n",
        f"Explore a collection of **{theme_title} Powers**: flavorful, ready-to-use monster abilities perfect for adding depth, danger, and thematic flair to your next encounter. These handcrafted powers are designed to fit monsters of any level and are fully compatible with 5E. Use them to customize creatures, surprise your players, and bring your world to life. Foe Foundry uses these Powers to procedurally generate monsters that are both flavorful and mechanically sharp. Powers are selected based on theme, role, and CR to ensure every creature feels distinct and balanced. Whether you're building a custom boss or filling out an encounter, Powers are the core of what makes Foe Foundry monsters unforgettable.  \n"
        "\n  ",
        "[Browse all powers by theme](all.md)\n",
    ]

    for power in powers:
        lines.append(f"[[!{power.name}]]")
        lines.append("---\n")

    return "\n".join(lines)


def generate_theme_file(theme: str, powers: list[PowerModel]):
    """Generate theme file and write directly to mkdocs_gen_files."""
    content = generate_theme_file_content(theme, powers)

    # Write it into the virtual MkDocs build
    with mkdocs_gen_files.open(f"powers/{theme}.md", "w") as f:
        f.write(content)

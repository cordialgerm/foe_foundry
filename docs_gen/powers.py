import mkdocs_gen_files

from foe_foundry_data.powers import PowerModel, Powers, PowerType


def generate_all_powers():
    # Create the index content
    lines = [
        "---",
        "title: All Powers",
        "description: Browse 600+ handcrafted monster powers for tabletop RPGs. Find unique abilities and build the perfect monster for your encounters.",
        "image: img/favicon.png",
        "---",
        "# All Monster Powers\n",
        "Monster Powers are the beating heart of Foe Foundry. Powers are flavorful, handcrafted abilities that make every 5E monster feel unique, dangerous, and ready for the table. Whether it's a venomous strike, a cursed aura, or a spell-laced scream, each Power is designed to challenge players and inspire GMs. Powers are organized by theme to help you discover exactly the right vibe for your next encounter, and they scale cleanly with CR so you can drop them into any campaign.  \n",
        "Foe Foundry automatically selects relevant powers for you basedd on the creature template that you're using, but you can also add or remove powers directly in the generator.  \n",
        f"Browse all {len(Powers.PowerLookup)} monster powers by theme below:\n",
    ]

    for power_type in PowerType.All():
        powers_by_theme = {
            t: [p for p in ps if p.power_type.lower() == power_type.lower()]
            for t, ps in Powers.PowersByTheme.items()
        }
        n = sum(len(p) for t, p in powers_by_theme.items())
        lines.append(f"## {power_type.title()} Powers ({n})\n")

        lines.append("<div class='list-with-columns'></div>\n")
        for theme, powers in powers_by_theme.items():
            if len(powers) == 0:
                continue

            lines.append(f"- [{theme.title()} Powers ({len(powers)})]({theme}.md)\n")

    for theme, powers in Powers.PowersByTheme.items():
        generate_theme_file(theme, powers)

    # Write it into the virtual MkDocs build
    with mkdocs_gen_files.open("powers/all.md", "w") as f:
        f.write("\n".join(lines))


def generate_theme_file(theme: str, powers: list[PowerModel]):
    lines = [
        "---",
        f"title: {theme.title()} Powers | Foe Foundry",
        f"description: Discover {len(powers)} {theme.lower()}-themed free powers for your next 5E or TTRPG monster.\n",
        "image: img/favicon.png",
        "---\n",
        f"# {theme.title()} Powers ({len(powers)})\n",
        f"Explore a collection of **{theme.title()} Powers**: flavorful, ready-to-use monster abilities perfect for adding depth, danger, and thematic flair to your next encounter. These handcrafted powers are designed to fit monsters of any level and are fully compatible with 5E. Use them to customize creatures, surprise your players, and bring your world to life. Foe Foundry uses these Powers to procedurally generate monsters that are both flavorful and mechanically sharp. Powers are selected based on theme, role, and CR to ensure every creature feels distinct and balanced. Whether you're building a custom boss or filling out an encounter, Powers are the core of what makes Foe Foundry monsters unforgettable.  \n"
        "\n  ",
        "[Browse all powers by theme](all.md)\n",
    ]

    for power in powers:
        lines.append(f"## {power.name}\n")
        for feature in power.features:
            lines.append(f"***{feature.name}***: {feature.description_md}")
            lines.append("\n")
        lines.append("---\n")

    # Write it into the virtual MkDocs build
    with mkdocs_gen_files.open(f"powers/{theme}.md", "w") as f:
        f.write("\n".join(lines))

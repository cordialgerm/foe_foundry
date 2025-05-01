import mkdocs_gen_files

from foe_foundry_data.powers import Powers


def generate_all_powers():
    # Create the index content
    lines = [
        "---",
        "title: All Powers",
        "---",
        "# All Powers\n",
        "Browse all monster powers below:\n",
    ]

    for theme, powers in Powers.PowersByTheme.items():
        lines.append(f"## {theme.title()} Powers\n")

        for power in powers:
            lines.append(f"### {power.name}\n")
            for feature in power.features:
                lines.append(f"***{feature.name}***: {feature.description_md}")
                lines.append("\n")

        lines.append("---")

    # Write it into the virtual MkDocs build
    with mkdocs_gen_files.open("powers/all.md", "w") as f:
        f.write("\n".join(lines))

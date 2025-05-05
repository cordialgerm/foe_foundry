import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.figure import Figure

from foe_foundry.creatures import (
    GenerationSettings,
    Monster,
    MonsterTemplate,
    MonsterVariant,
    SelectionSettings,
)


def plot_simulation(
    *,
    template: MonsterTemplate,
    variant: MonsterVariant,
    monster: Monster | None = None,
    n: int,
    temperature: float = 1.0,
    full_plot: bool = False,
) -> Figure:
    if monster is None:
        monster = variant.monsters[-1]

    counts = {}
    for i in range(n):
        rng = np.random.default_rng(20240711 + i)

        settings = GenerationSettings(
            rng=rng,
            creature_name=monster.name,
            monster_template=template.name,
            monster_key=monster.key,
            cr=monster.cr,
            is_legendary=monster.is_legendary,
            variant=variant,
            selection_settings=SelectionSettings(temperature=temperature),
        )
        stats = template.generate(settings)
        for power in stats.powers.selection.selected_powers:
            if power.name in counts:
                counts[power.name] += 1
            else:
                counts[power.name] = 1

    all_powers = stats.powers.all_powers
    power_lookup = {power.name: power for power in all_powers}

    names = []
    counters = []
    for name, count in counts.items():
        names.append(name)
        counters.append(count)

    types = [power_lookup[name].power_type for name in names]
    power_levels = [power_lookup[name].power_level_text for name in names]
    themes = [power_lookup[name].theme for name in names]

    df = pd.DataFrame(
        dict(
            names=names,
            counts=counters,
            types=types,
            power_levels=power_levels,
            themes=themes,
        )
    )
    df = df.sort_values(by="counts", ascending=False)

    if full_plot:
        fig, (ax1, ax2, ax3) = plt.subplots(nrows=3, figsize=(12, 12))
    else:
        fig, ax1 = plt.subplots(nrows=1, figsize=(12, 4))

    sns.barplot(data=df, x="names", y="counts", hue="types", ax=ax1)
    ax1.set_xticklabels(ax1.get_xticklabels(), rotation=90)

    if full_plot:
        # group by theme and generate count of each theme
        by_theme = (
            df.groupby("themes")
            .agg({"counts": "sum"})
            .sort_values(by="counts", ascending=False)
        )
        sns.barplot(data=by_theme, x=by_theme.index, y="counts", ax=ax2)
        ax2.set_xticklabels(ax2.get_xticklabels(), rotation=90)

        # group by power level and generate count of each power level
        by_power_level = (
            df.groupby("power_levels")
            .agg({"counts": "sum"})
            .sort_values(by="counts", ascending=False)
        )
        sns.barplot(data=by_power_level, x=by_power_level.index, y="counts", ax=ax3)

    fig.suptitle(f"{monster.name} - Temperature {temperature:.1f}")
    fig.tight_layout(h_pad=2)
    return fig

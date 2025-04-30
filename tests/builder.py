from io import BytesIO
from typing import cast

import ipywidgets as widgets
import numpy as np
from IPython.display import HTML, DisplayHandle, Markdown, display
from IPython.display import Image as IPythonImage
from PIL import Image

from foe_foundry.creatures import (
    AllTemplates,
    CreatureTemplate,
    CreatureVariant,
    GenerationSettings,
    SelectionSettings,
    SuggestedCr,
)
from foe_foundry.powers import AllPowers
from foe_foundry.templates import render_html_inline
from foe_foundry.utils import name_to_key


def get_all_power_keys() -> list[str]:
    k = [p.key for p in AllPowers]
    unique_k = set(k)
    if len(k) != len(unique_k):
        raise ValueError("Duplicate keys found")

    return sorted(unique_k)


def get_all_power_themes() -> list[str]:
    return sorted({p.theme_key for p in AllPowers if p.theme_key is not None})


def display_stat_builder() -> DisplayHandle | None:
    template_select = widgets.Dropdown(
        options=[t.name for t in AllTemplates],
        value=AllTemplates[0].name,
        description="Template:",
    )
    variant_select = widgets.Dropdown(description="Variants:")
    species_select = widgets.Dropdown(description="Species:")
    temperature_slider = widgets.FloatSlider(
        value=1.0,
        min=0,
        max=5,
        step=0.1,
        description="Temperature",
        readout=True,
        readout_format=".1f",
    )
    hp_slider = widgets.FloatSlider(
        value=1.0,
        min=0.5,
        max=2.0,
        step=0.1,
        description="HP",
        readout=True,
        readout_format=".2%",
    )
    damage_slider = widgets.FloatSlider(
        value=1.0,
        min=0.5,
        max=2.0,
        step=0.1,
        description="Damage",
        readout=True,
        readout_format=".2%",
    )
    theme_boost = widgets.SelectMultiple(
        options=get_all_power_themes(), value=[], description="Theme", rows=20
    )
    power_boost = widgets.Text(description="Power")
    render_button = widgets.Button(description="Render")
    random_theme_button = widgets.Button(description="Render with Random Theme")

    output = widgets.Output()

    variant_lookup: dict[str, tuple[CreatureVariant, SuggestedCr]] = {}
    variant_options: list[tuple[str, str]] = []

    def update_variant_select():
        template: CreatureTemplate = AllTemplates[cast(int, template_select.index)]
        variant_lookup.clear()
        variant_options.clear()
        for v in template.variants:
            for cr in v.suggested_crs:
                key = f"{v.key}-{cr.key}"
                variant_lookup[key] = (v, cr)
                variant_options.append((f"{cr.name} (CR {cr.cr})", key))

        variant_select.options = variant_options
        variant_select.index = 0

    def update_species_select():
        template: CreatureTemplate = AllTemplates[cast(int, template_select.index)]
        species_select.options = [s.name for s in template.species]
        if len(species_select.options):
            species_select.index = 0

    def rng_factory():
        return np.random.default_rng()

    def on_template_changed(change):
        update_variant_select()
        update_species_select()

    def on_button_clicked(b):
        generate_stats()

    def on_random_theme_button_clicked(b):
        themes = get_all_power_themes()
        rng = np.random.default_rng()
        i = rng.choice(len(themes))
        theme_boost.value = [themes[i]]

        generate_stats()

    def generate_stats():
        template: CreatureTemplate = AllTemplates[cast(int, template_select.index)]
        variant_index = cast(int, variant_select.index)
        _, variant_key = variant_options[variant_index]
        variant, suggested_cr = variant_lookup[variant_key]

        if power_boost.value:
            power_boosts = {name_to_key(p): 10.0 for p in power_boost.value.split(",")}
        else:
            power_boosts: dict[str, float] = {}

        theme_boosts = {str(v): 2.5 for v in theme_boost.value}

        species = (
            template.species[cast(int, species_select.index)]
            if len(template.species)
            else None
        )
        name = suggested_cr.name
        cr = suggested_cr.cr
        temperature = temperature_slider.value
        hp_multiplier = hp_slider.value
        damage_multiplier = damage_slider.value

        stats = template.generate(
            GenerationSettings(
                creature_name=name,
                creature_template=template.name,
                variant=variant,
                cr=cr,
                species=species,
                is_legendary=suggested_cr.is_legendary,
                selection_settings=SelectionSettings(
                    temperature=temperature,
                    boost_themes=theme_boosts,
                    boost_powers=power_boosts,
                ),
                rng=rng_factory(),
                hp_multiplier=hp_multiplier,
                damage_multiplier=damage_multiplier,
            )
        ).finalize()
        html = render_html_inline(stats)

        output.clear_output(wait=True)
        output.append_display_data(HTML(data=html))

        images = template.image_urls.get(variant.key, [])
        for path in images:
            img = Image.open(path)

            if img.height >= img.width and img.height > 500:
                new_width = int(500.0 / img.height * img.width)
                img.thumbnail((new_width, 500))
            elif img.width >= img.height and img.width > 500:
                new_height = int(500.0 / img.width * img.height)
                img.thumbnail((500, new_height))

            io = BytesIO()
            img.save(io, format="PNG")
            io.seek(0)
            output.append_display_data(IPythonImage(data=io.getbuffer()))

        output.append_display_data(Markdown(template.lore_md))

    render_button.on_click(on_button_clicked)
    random_theme_button.on_click(on_random_theme_button_clicked)
    template_select.observe(on_template_changed, names="value")

    update_variant_select()
    update_species_select()

    display(
        template_select,
        species_select,
        variant_select,
        hp_slider,
        damage_slider,
        temperature_slider,
        power_boost,
        theme_boost,
        render_button,
        random_theme_button,
        output,
    )

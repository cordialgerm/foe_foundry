from typing import cast

import ipywidgets as widgets
import numpy as np
from IPython.display import DisplayHandle, display, display_html

from foe_foundry.creatures import (
    AllTemplates,
    CreatureTemplate,
    CreatureVariant,
    GenerationSettings,
    SelectionSettings,
    SuggestedCr,
)
from foe_foundry.templates import render_html_inline


def display_stat_builder() -> DisplayHandle | None:
    template_select = widgets.Dropdown(
        options=[t.name for t in AllTemplates],
        value=AllTemplates[0].name,
        description="Template:",
    )
    variant_select = widgets.Dropdown(description="Variants:")
    species_select = widgets.Dropdown(description="Species:")
    render_button = widgets.Button(description="Render")
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

    def on_button_clicked(b):
        output.clear_output()

        template: CreatureTemplate = AllTemplates[cast(int, template_select.index)]

        template: CreatureTemplate = AllTemplates[cast(int, template_select.index)]
        variant_index = cast(int, variant_select.index)
        _, variant_key = variant_options[variant_index]
        variant, suggested_cr = variant_lookup[variant_key]

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
                variant=variant,
                cr=cr,
                species=species,
                selection_settings=SelectionSettings(temperature=temperature),
                rng=rng_factory(),
                hp_multiplier=hp_multiplier,
                damage_multiplier=damage_multiplier,
            )
        ).finalize()
        html = render_html_inline(stats)

        with output:
            display_html(html, raw=True)

    def on_template_changed(change):
        update_variant_select()
        update_species_select()

    render_button.on_click(on_button_clicked)
    template_select.observe(on_template_changed, names="value")

    update_variant_select()
    update_species_select()
    output.clear_output()

    return display(
        template_select,
        species_select,
        variant_select,
        hp_slider,
        damage_slider,
        temperature_slider,
        render_button,
        output,
    )

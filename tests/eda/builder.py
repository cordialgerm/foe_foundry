from typing import cast

import ipywidgets as widgets
import numpy as np
from IPython.display import DisplayHandle, display, display_html

from foe_foundry.creatures import AllTemplates, CreatureTemplate
from foe_foundry.templates import render_html_inline


def display_stat_builder() -> DisplayHandle | None:
    template_select = widgets.Dropdown(
        options=[t.name for t in AllTemplates],
        value=AllTemplates[0].name,
        description="Template:",
    )
    variant_select = widgets.Dropdown(description="Variants:")
    cr_select = widgets.Dropdown(description="CR:")
    species_select = widgets.Dropdown(description="Species:")
    render_button = widgets.Button(description="Render")
    output = widgets.Output()

    def update_variant_select():
        template: CreatureTemplate = AllTemplates[cast(int, template_select.index)]
        variants = template.variants
        variant_select.options = [v.name for v in variants]
        variant_select.index = 0

    def update_species_select():
        template: CreatureTemplate = AllTemplates[cast(int, template_select.index)]
        species_select.options = [s.name for s in template.species]
        if len(species_select.options):
            species_select.index = 0

    def update_cr_select():
        template: CreatureTemplate = AllTemplates[cast(int, template_select.index)]
        variant = template.variants[cast(int, variant_select.index)]
        cr_select.options = [
            (f"{cr.name} (CR {cr.cr})", cr.name) for cr in variant.suggested_crs
        ]
        cr_select.index = 0

    def rng_factory():
        return np.random.default_rng()

    def on_button_clicked(b):
        output.clear_output()

        template: CreatureTemplate = AllTemplates[cast(int, template_select.index)]

        variant = template.variants[cast(int, variant_select.index)]
        suggested_cr = variant.suggested_crs[cast(int, cr_select.index)]
        species = (
            template.species[cast(int, species_select.index)]
            if len(template.species)
            else None
        )
        name = suggested_cr.name
        cr = suggested_cr.cr

        stats = template.generate(
            name=name,
            variant_name=variant.name,
            cr=cr,
            species_name=species.name if species else None,
            rng_factory=rng_factory,
        ).finalize()
        html = render_html_inline(stats)

        with output:
            display_html(html, raw=True)

    def on_template_changed(change):
        update_variant_select()
        update_species_select()

    def on_variant_changed(change):
        update_cr_select()

    render_button.on_click(on_button_clicked)
    template_select.observe(on_template_changed, names="value")
    variant_select.observe(on_variant_changed, names="value")

    update_variant_select()
    update_species_select()
    update_cr_select()

    return display(
        template_select,
        species_select,
        variant_select,
        cr_select,
        render_button,
        output,
    )

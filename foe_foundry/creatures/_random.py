from typing import Callable, TypeAlias

import numpy as np

from ._all import AllTemplates
from .template import (
    CreatureSpecies,
    CreatureTemplate,
    CreatureVariant,
    GenerationSettings,
    SuggestedCr,
)

TemplateFilter: TypeAlias = Callable[[CreatureTemplate], bool]
VariantFilter: TypeAlias = Callable[[CreatureVariant], bool]
SpeciesFilter: TypeAlias = Callable[[CreatureSpecies], bool]
SuggestedCrFilter: TypeAlias = Callable[[SuggestedCr], bool]


def random_template_and_settings(
    rng: np.random.Generator,
    filter_templates: TemplateFilter | None = None,
    filter_variants: VariantFilter | None = None,
    filter_suggested_crs: SuggestedCrFilter | None = None,
    species_filter: SpeciesFilter | None = None,
) -> tuple[CreatureTemplate, GenerationSettings]:
    """Returns a random template and its settings"""

    if filter_templates is None:
        templates = AllTemplates
    else:
        templates = [t for t in AllTemplates if filter_templates(t)]

    template_index = rng.choice(len(templates))
    template = templates[template_index]

    if filter_variants is None:
        variants = template.variants
    else:
        variants = [v for v in template.variants if filter_variants(v)]

    variant_index = rng.choice(len(variants))
    variant = variants[variant_index]

    if template.species is None or len(template.species) == 0:
        species_options = [None]
    elif species_filter is None:
        species_options = template.species
    else:
        species_options = [s for s in template.species if species_filter(s)]

    species_index = rng.choice(len(species_options))
    species = species_options[species_index]

    if filter_suggested_crs is None:
        suggested_crs = variant.suggested_crs
    else:
        suggested_crs = [cr for cr in variant.suggested_crs if filter_suggested_crs(cr)]
    suggested_cr_index = rng.choice(len(suggested_crs))
    suggested_cr = suggested_crs[suggested_cr_index]

    settings = GenerationSettings(
        creature_name=suggested_cr.name,
        creature_template=template.name,
        cr=suggested_cr.cr,
        is_legendary=suggested_cr.is_legendary,
        variant=variant,
        species=species,
        rng=rng,
    )

    return template, settings

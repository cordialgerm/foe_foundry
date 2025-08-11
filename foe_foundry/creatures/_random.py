from typing import Callable, TypeAlias

import numpy as np

from ._all import AllTemplates
from ._template import (
    CreatureSpecies,
    GenerationSettings,
    Monster,
    MonsterTemplate,
    MonsterVariant,
)

TemplateFilter: TypeAlias = Callable[[MonsterTemplate], bool]
VariantFilter: TypeAlias = Callable[[MonsterVariant], bool]
SpeciesFilter: TypeAlias = Callable[[CreatureSpecies], bool]
MonsterFilter: TypeAlias = Callable[[Monster], bool]


def random_template_and_settings(
    rng: np.random.Generator,
    filter_templates: TemplateFilter | None = None,
    filter_variants: VariantFilter | None = None,
    filter_monsters: MonsterFilter | None = None,
    species_filter: SpeciesFilter | None = None,
) -> tuple[MonsterTemplate, GenerationSettings]:
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

    if filter_monsters is None:
        monsters = variant.monsters
    else:
        monsters = [cr for cr in variant.monsters if filter_monsters(cr)]
    monster_index = rng.choice(len(monsters))
    monster = monsters[monster_index]

    settings = GenerationSettings(
        creature_name=monster.name,
        monster_template=template.name,
        monster_key=monster.key,
        cr=monster.cr,
        is_legendary=monster.is_legendary,
        variant=variant,
        monster=monster,
        species=species,
        rng=rng,
    )

    return template, settings

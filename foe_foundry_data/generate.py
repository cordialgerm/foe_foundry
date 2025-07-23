import numpy as np

from foe_foundry.creatures import Monster, MonsterVariant, Statblock
from foe_foundry_data.refs import MonsterRef, MonsterRefResolver


def generate_monster(
    template_or_variant_key: str,
    ref_resolver: MonsterRefResolver,
    rng: np.random.Generator,
    **kwargs,
) -> tuple[MonsterRef | None, Statblock | None]:
    """Generates a monster based on the provided template or variant key."""

    ref = ref_resolver.resolve_monster_ref(template_or_variant_key)
    if ref is None:
        return None, None

    if ref.monster is None:
        options = []
        for variant in ref.template.variants:
            for monster in variant.monsters:
                options.append((variant, monster))

        index = rng.choice(len(options))
        variant, monster = options[index]
        ref = ref.copy(variant=variant, monster=monster)

    # we know these values aren't None because we checked above
    template = ref.template
    variant: MonsterVariant = ref.variant  # type: ignore
    monster: Monster = ref.monster  # type: ignore
    species = ref.species

    stats = template.generate_monster(
        variant=variant, monster=monster, species=species, rng=rng, **kwargs
    ).finalize()
    return ref, stats

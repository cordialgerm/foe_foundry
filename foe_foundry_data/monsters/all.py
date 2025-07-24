import os
from functools import cached_property

from foe_foundry.creatures import AllTemplates
from foe_foundry.powers import Power
from foe_foundry_data.refs import MonsterRef, MonsterRefResolver

from .data import MonsterModel


class _MonsterCache:
    @cached_property
    def one_of_each_monster(self) -> list[MonsterModel]:
        base_url = os.environ.get("SITE_URL")
        if base_url is None:
            raise ValueError("SITE_URL environment variable is not set")

        monsters = []
        for template in AllTemplates:
            for variant in template.variants:
                for monster in variant.monsters:
                    species = None
                    stats = template.generate_monster(
                        variant=variant, monster=monster, species=species
                    )
                    m = MonsterModel.from_monster(
                        stats=stats.finalize(),
                        template=template,
                        variant=variant,
                        monster=monster,
                        species=species,
                        base_url=base_url,
                    )
                    monsters.append(m)
        return monsters

    @cached_property
    def lookup(self) -> dict[str, MonsterModel]:
        return {monster.key: monster for monster in self.one_of_each_monster}


Monsters = _MonsterCache()


def monsters_for_power(power: Power) -> list[MonsterRef]:
    resolver = MonsterRefResolver()

    refs = []
    for monster in Monsters.one_of_each_monster:
        for loadout in monster.loadouts:
            for p in loadout.powers:
                if p.key == power.key:
                    ref = resolver.resolve_monster_ref(monster.name)
                    if ref is not None:
                        ref = ref.resolve()
                        refs.append(ref)

    def sort_by_name(ref: MonsterRef) -> str:
        return ref.monster.key if ref.monster is not None else ref.original_monster_name

    refs = sorted(refs, key=sort_by_name)
    return refs

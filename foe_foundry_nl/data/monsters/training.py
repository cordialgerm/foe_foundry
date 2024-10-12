from fnmatch import fnmatch

import numpy as np

from foe_foundry.creature_types import CreatureType

from .data import CanonicalMonster
from .load import get_canonical_monsters, name_to_key

# try to embed the monster roles from FoF and find similar and different creatures
# find similar and different creatures based on mental stats
# - try to embed the "Monster Roles" from FoF and see which creatures show up based on certain types of roles
# - create positive and negative examples based on monster roles. Ex: brutes should be dissimlar to spellcasters
# - create positive and negative examples based on creature stats. Ex: high intelligence creatures should be similar to each other and different from low intelligence creatures


LOW = 0.25
MED = 0.5
HIGH = 1


def _get_dragon_brood(color: str) -> list[str]:
    return [
        f"{color.title()} Dragon Wyrmling",
        f"Young {color.title()} Dragon",
        f"Adult {color.title()} Dragon",
        f"Ancient {color.title()} Dragon",
    ]


lineages = {
    "apes": ["Baboon", "Ape", "Giant Ape"],
    "bears": ["Black Bear", "Brown Bear", "Polar Bear"],
    "birds": ["Eagle", "Giant Eagle", "Hawk", "Blood Hawk", "Owl", "Raven"],
    "canines": [
        "Mastiff",
        "Wolf",
        "Dire Wolf",
        "Winter Wolf",
        "Werewolf",
        "Death Dog",
        "Blink Dog",
        "Hell Hound",
    ],
    "dinosaurs": [
        "Allosaurus",
        "Ankylosaurus",
        "Plesiosaurus",
        "Pteranodon",
        "Triceratops",
        "Tyrannosaurus Rex",
    ],
    "horses": ["Pony", "Draft Horse", "Riding Horse", "Warhorse", "Unicorn"],
    "spider": [
        "Giant Spider",
        "Giant Wolf Spider",
        "Phase Spider",
        "Spider",
        "Swarm of Insects (Spider)",
        "Drider",
    ],
    "familiars": [
        "Bat",
        "Cat",
        "Frog",
        "Hawk",
        "Lizard",
        "Octopus",
        "Owl",
        "Rat",
        "Raven",
        "Spider",
        "Weasel",
        "Imp",
        "Pseudodragon",
        "Quasit",
        "Skeleton",
        "Slaad Tadpole",
        "Sphinx of Wonder",
        "Sprite",
        "Venomous Snake",
    ],
    "criminals": ["Bandit", "Thug", "Spy", "Assassin"],
    "soldiers": ["Guard", "Veteran", "Knight", "Gladiator"],
    "cult": ["Cultist", "Cult Fanatic"],
    "priest": ["Acolyte", "Priest"],
    "kobold": ["*kobold*"],
    "townsfolk": ["Commoner", "Noble"],
    "outdoors": ["Scout", "Tribal Warrior", "Berserker", "Druid"],
    "goblinoids": ["Goblin", "Hobgoblin", "Bugbear", "*goblin*", "Orc", "*orc*"],
    "petrify": ["Cockatrice", "Medusa", "Gorgon", "Basilisk"],
    "mephit": ["*mephit*"],
    "gnoll": ["*gnoll*"],
    "hag": ["*hag*"],
    "spirit": [
        "Ghost",
        "Specter",
        "Wraith",
        "Will-o'-Wisp",
        "Wraith",
    ],
    "mage": ["Mage", "Archmage", "Lich", "*mage*"],
    "demon": [
        "Balor",
        "Dretch",
        "Glabrezu",
        "Hezrou",
        "Marilith",
        "Nalfeshnee",
        "Quasit",
        "Vrock",
        "Quasit",
    ],
    "devil": [
        "Lemure",
        "Imp",
        "Hell Hound",
        "Nightmare",
        "Chain Devil",
        "Bone Devil",
        "Horned Devil",
        "Erinyes",
        "Ice Devil",
        "Pit Fiend",
    ],
    "angel": ["Deva", "Planetar", "Solar"],
    "golem": ["*golem*"],
    "black_dragon": _get_dragon_brood("black"),
    "blue_dragon": _get_dragon_brood("blue"),
    "red_dragon": _get_dragon_brood("red"),
    "green_dragon": _get_dragon_brood("green"),
    "white_dragon": _get_dragon_brood("white"),
    "gold_dragon": _get_dragon_brood("gold"),
    "silver_dragon": _get_dragon_brood("silver"),
    "bronze_dragon": _get_dragon_brood("bronze"),
    "copper_dragon": _get_dragon_brood("copper"),
    "brass_dragon": _get_dragon_brood("brass"),
}


class SrdMonsterSelector:
    def __init__(self, rng: np.random.Generator):
        self.rng = rng

        canonical_monsters = get_canonical_monsters()
        self.srd_monsters = {k: m for k, m in canonical_monsters.items() if m.is_srd}
        self.keys = list(self.srd_monsters.keys())

        self.lineages: dict[str, set[str]] = {}
        for lineage, items in lineages.items():
            matches = set()
            for item in items:
                if "*" in item:
                    matches.update(
                        [
                            k
                            for k, v in self.srd_monsters.items()
                            if fnmatch(v.name, item)
                        ]
                    )
                else:
                    monster_key = name_to_key(item)
                    matches.add(self.srd_monsters[monster_key].key)
            self.lineages[lineage] = matches

        self.lineages_by_monster_key: dict[str, set[str]] = {}
        for lineage, keys in self.lineages.items():
            for key in keys:
                if key not in self.lineages_by_monster_key:
                    self.lineages_by_monster_key[key] = {lineage}
                else:
                    self.lineages_by_monster_key[key].add(lineage)

        self.monsters_by_creature_type: dict[str, set[str]] = {}
        for key, monster in self.srd_monsters.items():
            ct = CreatureType.parse(monster.creature_type).value
            if ct not in self.monsters_by_creature_type:
                self.monsters_by_creature_type[ct] = {key}
            else:
                self.monsters_by_creature_type[ct].add(key)

        self.similarities = {
            # aberrations are totally extra-planar
            CreatureType.Aberration: [],
            # beasts are natural - only kind of similar to monstrosities
            CreatureType.Beast: CreatureType.Monstrosity,
            # celestials are unique
            CreatureType.Celestial: [],
            # constructs are non-sentient created entities, similar to undead and elementals
            CreatureType.Construct: [CreatureType.Undead, CreatureType.Elemental],
            # dragons are unique
            CreatureType.Dragon: [],
            # elementals are created entities, similar to constructs
            CreatureType.Elemental: CreatureType.Construct,
            # fey have a sylvan/primal connection
            CreatureType.Fey: [
                CreatureType.Plant,
                CreatureType.Elemental,
                CreatureType.Beast,
            ],
            # fiends are pure evil, similar to undead
            CreatureType.Fiend: CreatureType.Undead,
            # giants are unique
            CreatureType.Giant: [],
            # humanoids could be related to gaints, fey, celestials, or dragons
            CreatureType.Humanoid: [
                CreatureType.Giant,
                CreatureType.Fey,
                CreatureType.Celestial,
                CreatureType.Dragon,
            ],
            # monstrosities are somewhat similar to beasts
            CreatureType.Monstrosity: CreatureType.Beast,
            # oozes are somewhat simlar to elementals
            CreatureType.Ooze: CreatureType.Elemental,
            # plants are somewhat similar to fey and elementals as primal entities
            CreatureType.Plant: [CreatureType.Fey, CreatureType.Elemental],
            # undead are somewhat similar to fiends and constructs
            CreatureType.Undead: [CreatureType.Fiend, CreatureType.Construct],
        }

    def random_positive_negative_triplet(self) -> tuple[str, str, str]:
        anchor = self._choose(self.keys)
        return self.get_positive_negative_triplet(anchor)

    def get_positive_negative_triplet(self, anchor: str) -> tuple[str, str, str]:
        try:
            anchor = name_to_key(anchor)
            anchor_monster = self.srd_monsters[anchor]
            ct = CreatureType.parse(anchor_monster.creature_type)
            lineages = self.lineages_by_monster_key.get(anchor, [])

            def _similar_ct():
                keys = self._similar_creature_types(
                    ct,
                    include_self=True,
                    exclude_keys={anchor},
                )
                return self._choose(keys)

            def _dissimilar_ct():
                keys = self._dissimilar_creature_types(
                    ct,
                    exclude_keys={anchor},
                )
                return self._choose(keys)

            def _similar_lineage():
                keys = set()
                for lineage in lineages:
                    keys.update(k for k in self.lineages[lineage] if k != anchor)
                return self._choose(list(keys))

            if len(lineages) == 0:
                similar = _similar_ct()
                dissimilar = _dissimilar_ct()
                return anchor, similar, dissimilar
            else:
                if self.rng.random() <= 0.5:
                    similar = _similar_ct()
                else:
                    similar = _similar_lineage()

                dissimilar = _dissimilar_ct()
                return anchor, similar, dissimilar
        except Exception as x:
            raise ValueError(f"Error getting triplet for {anchor}") from x

    def _similar_creature_types(
        self,
        ct: CreatureType,
        include_self: bool,
        exclude_keys: set[str],
    ) -> list[str]:
        similar: list[CreatureType] = self.similarities.get(ct, [])

        if callable(similar):
            monsters = [k for k, m in self.srd_monsters.items() if similar(m)]
            return monsters
        elif isinstance(similar, CreatureType):
            similar = [similar]

        if include_self:
            similar.append(ct)

        keys = set()
        for ct in similar:
            keys.update(self.monsters_by_creature_type[ct])

        keys = keys - exclude_keys
        return list(keys)

    def _dissimilar_creature_types(
        self, ct: CreatureType, exclude_keys: set[str]
    ) -> list[str]:
        all_keys = set(self.srd_monsters.keys())
        exclusions = self._similar_creature_types(
            ct, include_self=True, exclude_keys=exclude_keys
        )
        keys = all_keys - set(exclusions)
        return list(keys)

    def _choose(self, keys: list[str]):
        if len(keys) == 0:
            raise ValueError("Cannot choose from empty set")

        index = self.rng.choice(len(keys))
        return keys[index]

import re
from dataclasses import dataclass
from fnmatch import fnmatch

import numpy as np
from backports.strenum import StrEnum
from datasets import Dataset, DatasetDict

from foe_foundry.creature_types import CreatureType

from .load import get_canonical_monsters, load_canonical_monster_text, name_to_key

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


class SimilarityType(StrEnum):
    desc_to_statblock = "desc_to_statblock"
    desc_to_desc = "desc_to_desc"
    statblock_to_statblock = "statblock_to_statblock"


class SimilarityReason(StrEnum):
    same_creature = "same_creature"
    similar_creature_type = "similar_creature_type"
    similar_lineage = "similar_lineage"
    similar_ac = "similar_ac"
    similar_hp = "similar_hp"
    similar_cr = "similar_cr"


@dataclass(kw_only=True)
class TrainingTriplet:
    anchor: str
    positive: str
    negative: str
    reason: SimilarityReason
    type: SimilarityType

    def to_text(self) -> tuple[str, str, str]:
        raw_anchor = load_canonical_monster_text(self.anchor)
        raw_positive = load_canonical_monster_text(self.positive)
        raw_negative = load_canonical_monster_text(self.negative)

        if self.type == SimilarityType.desc_to_statblock:
            anchor_desc = self._get_summary(raw_anchor)
            positive_statblock = self._get_statblock(raw_positive)
            negative_statblock = self._get_statblock(raw_negative)
            return anchor_desc, positive_statblock, negative_statblock
        elif self.type == SimilarityType.desc_to_desc:
            anchor_desc = self._get_summary(raw_anchor)
            positive_desc = self._get_summary(raw_positive)
            negative_desc = self._get_summary(raw_negative)
            return anchor_desc, positive_desc, negative_desc
        elif self.type == SimilarityType.statblock_to_statblock:
            anchor_statblock = self._get_statblock(raw_anchor)
            positive_statblock = self._get_statblock(raw_positive)
            negative_statblock = self._get_statblock(raw_negative)
            return anchor_statblock, positive_statblock, negative_statblock
        else:
            raise NotImplementedError(f"Unknown similarity type: {self.type}")

    def _get_summary(self, text: str) -> str:
        # need to get just the description
        summary_pattern = re.compile(r"<summary>(.*?)</summary>", re.DOTALL)
        detail_pattern = re.compile(r"<detail>(.*?)</detail>", re.DOTALL)
        summaries = summary_pattern.findall(text)
        details = detail_pattern.findall(text)
        # TODO - pick random
        # TODO - mask monster's name ???
        return "\n\n".join(summaries + details)

    def _get_statblock(self, text: str) -> str:
        statblock_pattern = re.compile(r"<statblock>(.*?)</statblock>", re.DOTALL)
        results = statblock_pattern.findall(text)
        # TODO - pick random
        # TODO - mask monster's name ???
        return "\n\n".join(results)


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

    def random_positive_negative_triplets(self) -> list[TrainingTriplet]:
        anchor = self._choose(self.keys)
        triplets = self.get_positive_negative_triplets(anchor)
        return triplets

    def get_positive_negative_triplets(self, anchor: str) -> list[TrainingTriplet]:
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

            def _similar_cr():
                keys = self._similar_cr(anchor_monster.cr, {anchor})
                return self._choose(keys)

            def _dissimlar_cr():
                keys = self._dissimilar_cr(anchor_monster.cr, {anchor})
                return self._choose(keys)

            def _similar_ac():
                keys = self._similar_ac(anchor_monster.ac, {anchor})
                return self._choose(keys)

            def _dissimilar_ac():
                keys = self._dissimilar_ac(anchor_monster.ac, {anchor})
                return self._choose(keys)

            def _similar_hp():
                keys = self._similar_hp(anchor_monster.hp, {anchor})
                return self._choose(keys)

            def _dissimilar_hp():
                keys = self._dissimilar_hp(anchor_monster.hp, {anchor})
                return self._choose(keys)

            results: list[TrainingTriplet] = []

            try:
                # a creature to itself
                positive = anchor
                negative = _dissimilar_ct()
                for type in [
                    SimilarityType.desc_to_desc,
                    SimilarityType.desc_to_statblock,
                    SimilarityType.statblock_to_statblock,
                ]:
                    results.append(
                        TrainingTriplet(
                            anchor=anchor,
                            positive=positive,
                            negative=negative,
                            reason=SimilarityReason.same_creature,
                            type=type,
                        )
                    )
            except ValueError:
                pass

            try:
                # a creature to a similar creature type
                positive = _similar_ct()
                negative = _dissimilar_ct()
                for type in [
                    SimilarityType.desc_to_desc,
                    SimilarityType.desc_to_statblock,
                    SimilarityType.statblock_to_statblock,
                ]:
                    results.append(
                        TrainingTriplet(
                            anchor=anchor,
                            positive=positive,
                            negative=negative,
                            reason=SimilarityReason.similar_creature_type,
                            type=type,
                        )
                    )
            except ValueError:
                pass

            try:
                # a statblock with similar AC to another statblock
                results.append(
                    TrainingTriplet(
                        anchor=anchor,
                        positive=_similar_ac(),
                        negative=_dissimilar_ac(),
                        reason=SimilarityReason.similar_ac,
                        type=SimilarityType.statblock_to_statblock,
                    )
                )
            except ValueError:
                pass

            try:
                # a statblock with similar HP to another statblock
                results.append(
                    TrainingTriplet(
                        anchor=anchor,
                        positive=_similar_hp(),
                        negative=_dissimilar_hp(),
                        reason=SimilarityReason.similar_hp,
                        type=SimilarityType.statblock_to_statblock,
                    )
                )
            except ValueError:
                pass

            try:
                results.append(
                    TrainingTriplet(
                        anchor=anchor,
                        positive=_similar_cr(),
                        negative=_dissimlar_cr(),
                        reason=SimilarityReason.similar_cr,
                        type=SimilarityType.statblock_to_statblock,
                    )
                )
            except ValueError:
                pass

            if len(lineages):
                try:
                    # similar lineage
                    for type in [
                        SimilarityType.desc_to_desc,
                        SimilarityType.desc_to_statblock,
                        SimilarityType.statblock_to_statblock,
                    ]:
                        results.append(
                            TrainingTriplet(
                                anchor=anchor,
                                positive=_similar_lineage(),
                                negative=_dissimilar_ct(),
                                reason=SimilarityReason.similar_hp,
                                type=SimilarityType.statblock_to_statblock,
                            )
                        )
                except ValueError:
                    pass

            return results

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

    def _similar_ac(self, ac: int, exclude_keys: set[str]) -> list[str]:
        def is_similar(ac1: int, ac2: int):
            return abs(ac1 - ac2) <= 1

        keys = {k for k, m in self.srd_monsters.items() if is_similar(ac, m.ac)}
        keys = keys - exclude_keys
        return list(keys)

    def _dissimilar_ac(self, ac: int, exclude_keys: set[str]) -> list[str]:
        all_keys = set(self.srd_monsters.keys())
        exclusions = self._similar_ac(ac, exclude_keys)
        keys = all_keys - set(exclusions)
        return list(keys)

    def _similar_hp(self, hp: int, exclude_keys: set[str]) -> list[str]:
        def is_similar(hp1: int, hp2: int):
            if min(hp1, hp2) <= 10:
                return abs(hp1 - hp2) <= 2
            else:
                return abs(hp1 - hp2) / min(hp1, hp2) <= 0.15

        keys = {k for k, m in self.srd_monsters.items() if is_similar(hp, m.hp)}
        keys = keys - exclude_keys
        return list(keys)

    def _dissimilar_hp(self, hp: int, exclude_keys: set[str]) -> list[str]:
        all_keys = set(self.srd_monsters.keys())
        exclusions = self._similar_hp(hp, exclude_keys)
        keys = all_keys - set(exclusions)
        return list(keys)

    def _similar_cr(self, cr: str, exclude_keys: set[str]) -> list[str]:
        cr_float = float(cr)

        def is_similar(cr1: float, cr2: float):
            if cr1 <= 1:
                return cr1 == cr2
            elif cr1 <= 10:
                return abs(cr1 - cr2) <= 1
            elif cr1 <= 20:
                return abs(cr1 - cr2) <= 3
            else:
                return abs(cr1 - cr2) <= 6

        keys = {
            k
            for k, m in self.srd_monsters.items()
            if is_similar(cr_float, m.cr_numeric)
        }
        keys = keys - exclude_keys
        return list(keys)

    def _dissimilar_cr(self, cr: str, exclude_keys: set[str]) -> list[str]:
        all_keys = set(self.srd_monsters.keys())
        exclusions = self._similar_cr(cr, exclude_keys)
        keys = all_keys - set(exclusions)
        return list(keys)

    def _choose(self, keys: list[str]):
        if len(keys) == 0:
            raise ValueError("Cannot choose from empty set")

        index = self.rng.choice(len(keys))
        return keys[index]


def load_triplet_loss_dataset() -> tuple[DatasetDict, int, int, int]:
    rng = np.random.default_rng(20240711)
    selector = SrdMonsterSelector(rng)

    examples: list[dict] = []
    for _ in range(2000):
        triplets = selector.random_positive_negative_triplets()
        for triplet in triplets:
            anchor, positive, negative = triplet.to_text()
            examples.append(dict(anchor=anchor, positive=positive, negative=negative))
    n_examples = len(examples)

    n_test = n_eval = n_examples // 10
    n_train = n_examples - n_test - n_eval
    train_examples = examples[:n_train]
    eval_examples = examples[n_train : n_train + n_eval]
    test_examples = examples[n_train + n_eval :]

    train_dataset = Dataset.from_list(train_examples)
    eval_dataset = Dataset.from_list(eval_examples)
    test_dataset = Dataset.from_list(test_examples)

    return (
        DatasetDict(
            {
                "train": train_dataset,
                "eval": eval_dataset,
                "test": test_dataset,
            },
            field_names=["anchor", "positive", "negative"],
        ),
        n_train,
        n_eval,
        n_test,
    )

# from pathlib import Path
# from collections.abc import Iterable
# from datasets import Dataset, DatasetDict
# import math
# import numpy as np
# import json

# from .monsters import iter_all_monsters


# def load_dataset():
#     creature_types = load_5e_srd_creature_types()
#     descriptions = load_5e_srd_monster_descriptions()
#     monsters = [m.to_dict() for m in iter_all_monsters()]
#     spells = load_5e_srd_spells()
#     misc = load_5e_srd_misc_markdown_files() + load_lgmrd_misc_markdown_files()
#     all_data = monsters + spells + creature_types + descriptions + misc
#     print(f"Loaded {len(monsters)} monsters")
#     print(f"Loaded {len(spells)} spells")
#     print(f"Loaded {len(creature_types)} creature_types")
#     print(f"Loaded {len(descriptions)} descriptions")
#     print(f"Loaded {len(misc)} misc files")

#     rng = np.random.default_rng(20240711)
#     indexes = np.arange(len(all_data), dtype=int)
#     rng.shuffle(indexes)
#     n_test = math.floor(0.05 * len(all_data))

#     train_dataset = Dataset.from_list([all_data[i] for i in indexes[:n_test]])
#     test_dataset = Dataset.from_list([all_data[i] for i in indexes[n_test:]])

#     dataset = DatasetDict({"train": train_dataset, "test": test_dataset})
#     return dataset


# def iter_5e_srd_spells() -> Iterable[tuple[str, str]]:
#     dir = Path(__file__).parent.parent.parent / "data" / "5esrd" / "Spells"

#     for spell_file in dir.glob("*.md"):
#         with spell_file.open("r", encoding="utf-8") as f:
#             spell = spell_file.name[:-3]
#             text = f.read()
#             yield spell, text


# def load_5e_srd_spells() -> list[dict]:
#     all_data = []
#     for spell, text in iter_5e_srd_spells():
#         all_data.append(
#             dict(
#                 type="spell",
#                 spell_name=spell,
#                 text=f"<Entity>Spell</Entity><SpellName>{spell}</SpellName>.\n Description {text}",
#             )
#         )

#     return all_data


# def load_5e_srd_creature_types(repeats: int = 10) -> list[dict]:
#     path = (
#         Path(__file__).parent.parent.parent / "data" / "custom" / "creature_types.json"
#     )

#     items = []
#     with path.open("r", encoding="utf-8") as f:
#         creature_types = json.load(f)
#         for item in creature_types:
#             creature_type = item["creature_type"]
#             description = item["description"]
#             examples = item["examples"]
#             items.append(
#                 dict(
#                     type="creature_type",
#                     creature_type=creature_type,
#                     text=f"<Entity>CreatureType</Entity><CreatureType>{creature_type}</CreatureType>.\n Description: {description}. Examples: {examples}",
#                 )
#             )
#     return repeats * items


# def load_5e_srd_monster_descriptions() -> list[dict]:
#     path = (
#         Path(__file__).parent.parent.parent
#         / "data"
#         / "custom"
#         / "descriptions_5esrd.json"
#     )

#     items = []
#     with path.open("r", encoding="utf-8") as f:
#         creature_descriptions = json.load(f)
#         for descr in creature_descriptions:
#             name = descr["name"]
#             description = descr["description"]
#             items.append(
#                 dict(
#                     type="creature_description",
#                     name=name,
#                     text=f"<MonsterName>{name}</MonsterName>. Description: {description}.",
#                 )
#             )
#     return items


# def load_5e_srd_misc_markdown_files() -> list[dict]:
#     base_path = Path(__file__).parent.parent.parent / "data" / "5esrd"
#     exclude_dirs = ["Monsters", "Monsters (Alt)"]

#     markdown_files = []
#     for file_path in base_path.rglob("*.md"):
#         if not any(exclude_dir in file_path.parts for exclude_dir in exclude_dirs):
#             with file_path.open("r", encoding="utf-8") as f:
#                 try:
#                     text = f.read()
#                     markdown_files.append(dict(type="supporting_file", text=text))
#                 except Exception as x:
#                     print(f"UNABLE TO PARSE {file_path}. {x}")

#     return markdown_files


# def load_lgmrd_misc_markdown_files() -> list[dict]:
#     base_path = Path(__file__).parent.parent.parent / "data" / "lgmrd"
#     dirs = [
#         base_path / "markdown_obsidian_5e_monster_builder",
#         base_path / "markdown_obsidian",
#     ]

#     markdown_files = []
#     for dir in dirs:
#         for file_path in dir.rglob("*.md"):
#             with file_path.open("r", encoding="utf-8") as f:
#                 try:
#                     text = f.read()
#                     markdown_files.append(dict(type="supporting_file", text=text))
#                 except Exception as x:
#                     print(f"UNABLE TO PARSE {file_path}. {x}")

#     return markdown_files

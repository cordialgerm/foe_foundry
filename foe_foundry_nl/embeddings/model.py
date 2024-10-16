from functools import cached_property

import numpy as np

from ..data.monsters import CanonicalMonster, get_canonical_monsters
from ..model import get_model
from .data import MonsterEmbeddings


class _Loader:
    @property
    def monsters(self) -> dict[str, CanonicalMonster]:
        return get_canonical_monsters()

    @cached_property
    def embeddings(self) -> MonsterEmbeddings:
        keys = list(self.monsters.keys())
        return get_embeddings(keys)


_loader = _Loader()


def get_embedding(key: str) -> MonsterEmbeddings:
    monster = _loader.monsters[key]
    model = get_model()

    text = monster.as_markdown()
    embedding = model.encode(text, convert_to_numpy=True)
    keys = np.asarray([key], dtype=str)
    embeddings = embedding[np.newaxis, :]
    return MonsterEmbeddings(keys=keys, embeddings=embeddings)


def get_embeddings(keys: list[str]) -> MonsterEmbeddings:
    monsters = [_loader.monsters[key] for key in keys]
    model = get_model()

    texts = [monster.as_markdown() for monster in monsters]
    embeddings = model.encode(sentences=texts, convert_to_numpy=True)
    return MonsterEmbeddings(keys=np.asarray(keys, dtype=str), embeddings=embeddings)


def get_all_embeddings() -> MonsterEmbeddings:
    return _loader.embeddings

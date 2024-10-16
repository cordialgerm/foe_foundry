from dataclasses import dataclass

import numpy as np

from ..data.monsters import CanonicalMonster, get_canonical_monsters, name_to_key
from ..embeddings import embedding_distance, embedding_similarity, get_all_embeddings
from ..model import get_model


@dataclass
class SimilarMonster:
    monster: CanonicalMonster
    similarity: float


@dataclass
class ClosestMonster:
    monster: CanonicalMonster
    distance: float


def find_closest_monsters(
    monster_name: str, limit: int = 5, srd_only: bool = False
) -> list[ClosestMonster]:
    all_embeddings = get_all_embeddings()
    monsters = get_canonical_monsters()
    key = name_to_key(monster_name)

    monster_embedding = all_embeddings.get_embedding(key)

    if srd_only:
        indexes = np.array(
            [i for i, k in enumerate(all_embeddings.keys) if monsters[k].is_srd]
        )
        keys = all_embeddings.keys[indexes]
        embeddings = all_embeddings.embeddings[indexes]
    else:
        indexes = np.arange(all_embeddings.n, dtype=int)
        keys = all_embeddings.keys
        embeddings = all_embeddings.embeddings

    distances = embedding_distance(
        monster_embedding[np.newaxis, :], embeddings
    ).flatten()

    indexes = np.argsort(distances)
    closest_indexes = indexes[: limit + 1]  # includes self

    similar_monsters = []
    for index in closest_indexes:
        similar_key: str = str(keys[index])
        if similar_key == key:
            continue

        monster = monsters[similar_key]
        distance = float(distances[index])
        similar_monsters.append(ClosestMonster(monster=monster, distance=distance))

    return similar_monsters


def find_similar_monsters_from_description(
    description: str, limit: int = 5, srd_only: bool = False
) -> list[SimilarMonster]:
    model = get_model()
    monsters = get_canonical_monsters()

    query_embedding = model.encode(description, convert_to_numpy=True)

    if srd_only:
        all_embeddings = get_all_embeddings()
        indexes = np.array(
            [i for i, k in enumerate(all_embeddings.keys) if monsters[k].is_srd]
        )
        keys = all_embeddings.keys[indexes]
        embeddings = all_embeddings.embeddings[indexes]
    else:
        all_embeddings = get_all_embeddings()
        indexes = np.arange(all_embeddings.n, dtype=int)
        keys = all_embeddings.keys

    similarities = embedding_similarity(
        query_embedding[np.newaxis, :], embeddings
    ).flatten()
    sorted_indexes = np.argsort(similarities)[::-1]
    closest_indexes = sorted_indexes[:limit]

    similar_monsters = []
    for i in closest_indexes:
        key = str(keys[i])
        monster = monsters[key]
        similarity = float(similarities[i])
        similar_monsters.append(SimilarMonster(monster=monster, similarity=similarity))
    return similar_monsters

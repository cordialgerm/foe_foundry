from __future__ import annotations

import base64
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import numpy.typing as npt
from sklearn.metrics.pairwise import cosine_similarity, euclidean_distances


@dataclass
class MonsterEmbeddings:
    keys: npt.NDArray[np.str_]  #  [monsters]
    embeddings: npt.NDArray[np.float32]  # [monsters, embedding_size]

    def __post_init__(self):
        self._lookup = {key: i for i, key in enumerate(self.keys)}

    def key_index(self, key: str) -> int:
        return self._lookup[key]

    def sort(self, keys: list[str]) -> MonsterEmbeddings:
        lookup = {key: i for i, key in enumerate(self.keys)}
        indices = [lookup[key] for key in keys]
        return MonsterEmbeddings(
            keys=np.copy(self.keys[indices]),
            embeddings=np.copy(self.embeddings[indices]),
        )

    def __getitem__(self, indexes: np.ndarray | int) -> npt.NDArray[np.float32]:
        return self.embeddings[indexes, :]

    @property
    def n(self) -> int:
        return len(self.keys)

    def __len__(self) -> int:
        return self.n


def embedding(key: str) -> MonsterEmbeddings:
    path = (
        Path(__file__).parent.parent / "data" / "5e_canonical_embeddings" / f"{key}.txt"
    )
    text = path.read_text()
    buffer = base64.b64decode(text)
    base64_embedding = np.frombuffer(buffer, dtype=np.float32)
    return MonsterEmbeddings(
        keys=np.array([key], dtype=str), embeddings=base64_embedding[np.newaxis, :]
    )


def embeddings(keys: list[str], skip_if_missing: bool = False) -> MonsterEmbeddings:
    base_dir = Path(__file__).parent.parent
    dir = base_dir / "data" / "5e_canonical_embeddings"

    embeddings = []
    used_keys = []
    for key in keys:
        path = dir / f"{key}.txt"

        if skip_if_missing and not path.exists():
            continue
        elif not path.exists():
            raise ValueError(
                f"Missing embedding for {key}. Searched {path.relative_to(base_dir)}"
            )

        text = path.read_text()
        buffer = base64.b64decode(text)
        base64_embedding = np.frombuffer(buffer, dtype=np.float32)
        embeddings.append(base64_embedding)
        used_keys.append(key)

    embeddings = np.array(embeddings, dtype=np.float32)
    return MonsterEmbeddings(
        keys=np.asarray(used_keys, dtype=str), embeddings=embeddings
    )


def all_embeddings() -> MonsterEmbeddings:
    dir = Path(__file__).parent.parent / "data" / "5e_canonical_embeddings"
    keys = [p.stem for p in dir.glob("*.txt")]
    return embeddings(keys)


def similarity(
    embedding1: npt.NDArray[np.float32], embedding2: npt.NDArray[np.float32]
) -> npt.NDArray[np.float32]:
    return cosine_similarity(embedding1, embedding2)


def distance(
    embedding1: npt.NDArray[np.float32], embedding2: npt.NDArray[np.float32]
) -> npt.NDArray[np.float32]:
    return euclidean_distances(embedding1, embedding2)

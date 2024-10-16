from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import numpy.typing as npt


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

    def get_embedding(self, key: str) -> npt.NDArray[np.float32]:
        index = self.key_index(key)
        return self.embeddings[index, :]

    @property
    def n(self) -> int:
        return len(self.keys)

    def __len__(self) -> int:
        return self.n

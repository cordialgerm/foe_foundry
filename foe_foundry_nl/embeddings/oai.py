from __future__ import annotations

import base64
from pathlib import Path

import numpy as np

from .data import MonsterEmbeddings


def load_oai_embedding(key: str) -> MonsterEmbeddings:
    path = (
        Path(__file__).parent.parent / "data" / "5e_canonical_embeddings" / f"{key}.txt"
    )
    text = path.read_text()
    buffer = base64.b64decode(text)
    base64_embedding = np.frombuffer(buffer, dtype=np.float32)
    return MonsterEmbeddings(
        keys=np.array([key], dtype=str), embeddings=base64_embedding[np.newaxis, :]
    )


def load_oai_embeddings(
    keys: list[str], skip_if_missing: bool = False
) -> MonsterEmbeddings:
    base_dir = Path(__file__).parent.parent.parent
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


def load_all_oai_embeddings() -> MonsterEmbeddings:
    dir = Path(__file__).parent.parent.parent / "data" / "5e_canonical_embeddings"
    keys = [p.stem for p in dir.glob("*.txt")]
    return load_oai_embeddings(keys)

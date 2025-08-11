from collections.abc import Iterable
from pathlib import Path

import numpy as np
from datasets import Dataset, DatasetDict

from ..embeddings import (
    MonsterEmbeddings,
    embedding_similarity,
    load_all_oai_embeddings,
)
from .background import iter_background_info
from .monsters2 import MonsterInfo, get_monsters, iter_monster_paragraphs
from .paragraph import TrainingParagraph


def load_mlm_dataset() -> DatasetDict:
    rng = np.random.default_rng(20240711)
    p_train = 0.8
    p_eval = 0.1

    train = []
    test = []
    eval = []

    for p in _iter_all_paragraphs():
        doc = p.to_dict()
        r = rng.random()
        if r <= p_train:
            train.append(doc)
        elif r <= p_train + p_eval:
            test.append(doc)
        else:
            eval.append(doc)

    train_dataset = Dataset.from_list(train)
    test_dataset = Dataset.from_list(test)
    eval_dataset = Dataset.from_list(eval)

    return DatasetDict(
        {
            "train": train_dataset,
            "eval": eval_dataset,
            "test": test_dataset,
        }
    )


def load_triplet_loss_dataset() -> DatasetDict:
    rng = np.random.default_rng(20240711)

    train_examples = []
    test_examples = []
    eval_examples = []

    for triplets in _iter_triplets(rng):
        r = rng.random()
        for anchor, positive, negative in triplets:
            item = dict(anchor=anchor, positive=positive, negative=negative)

            if r <= 0.8:
                train_examples.append(item)
            elif r <= 0.9:
                test_examples.append(item)
            else:
                eval_examples.append(item)

    rng.shuffle(train_examples)
    rng.shuffle(test_examples)
    rng.shuffle(eval_examples)

    train_dataset = Dataset.from_list(train_examples)
    test_dataset = Dataset.from_list(test_examples)
    eval_dataset = Dataset.from_list(eval_examples)

    return DatasetDict(
        {
            "train": train_dataset,
            "eval": eval_dataset,
            "test": test_dataset,
        },
        field_names=["anchor", "positive", "negative"],
    )


def _iter_triplets(rng: np.random.Generator) -> Iterable[list[tuple[str, str, str]]]:
    monsters = get_monsters()
    embeddings = load_all_oai_embeddings()

    # for each monster, use its queries as the anchors
    # its paragraphs are then the positives
    # choose a "hard" negative by finding another similar monster with cosine similarity of 0.4-0.7

    for key, monster in monsters.items():
        anchors = monster.test_queries
        positives = []
        for _, positive in monster.iter_paragraphs(rng):
            positives.append(positive)

        try:
            negatives = _find_hard_negatives(monsters, embeddings, rng, key)
        except KeyError:
            print(f"Could not find hard negatives for {key}")
            continue

        triplets = []
        for anchor in anchors:
            for positive in positives:
                for negative in negatives:
                    triplets.append((anchor, positive, negative))
        yield triplets


def _find_hard_negatives(
    monsters: dict[str, MonsterInfo],
    embeddings: MonsterEmbeddings,
    rng: np.random.Generator,
    key: str,
    n: int = 5,
) -> list[str]:
    embedding = embeddings.get_embedding(key)

    # find other monsters
    other_keys = np.array(
        [
            other_key
            for other_key, _ in monsters.items()
            if other_key != key and other_key in embeddings
        ]
    )
    other_embeddings = np.array(
        [embeddings.get_embedding(other_key) for other_key in other_keys],
        dtype=np.float32,
    )

    # calculate cosine similarities
    # we want to find "hard" negatives, which are monsters that are superficially similar but have a key difference
    # we are going to interpret that as a cosine similarity of 0.4 to 0.7
    # having similarity below 0.4 means it is too different, which is a "soft negative"
    # similarity above 0.7 means it is too similar, so it would be a positive and not a negative
    similarities = embedding_similarity(
        embedding[np.newaxis, :], other_embeddings
    ).flatten()

    lb = 0.6
    ub = 0.7
    indexes = (lb <= similarities) & (similarities <= ub)

    selection_weight = np.zeros_like(other_keys, dtype=np.float32)
    selection_weight[indexes] = np.exp(100 * (similarities[indexes] - lb))
    selection_weight = selection_weight / np.sum(selection_weight)

    hard_negatives = rng.choice(other_keys, p=selection_weight, size=n, replace=False)

    negative_paragraphs = []
    for hard_negative in hard_negatives:
        monster = monsters[hard_negative]
        monster_paragraphs = [p for _, p in monster.iter_paragraphs(rng)]
        negative = str(rng.choice(monster_paragraphs, size=None))
        negative_paragraphs.append(negative)

    return negative_paragraphs


def _iter_all_paragraphs() -> Iterable[TrainingParagraph]:
    yield from iter_background_info()
    yield from iter_monster_paragraphs()


if __name__ == "__main__":
    infos = np.array([i.word_count for i in iter_background_info()])

    print(f"Loaded {len(infos)} background documents")
    print(f"Total Word Count of {np.sum(infos):,.0f}")
    print(f"Average Word Count of {np.mean(infos):.2f}")

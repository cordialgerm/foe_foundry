import numpy as np
import numpy.typing as npt
from sklearn.metrics.pairwise import cosine_similarity, euclidean_distances


def embedding_similarity(
    embedding1: npt.NDArray[np.float32], embedding2: npt.NDArray[np.float32]
) -> npt.NDArray[np.float32]:
    return cosine_similarity(embedding1, embedding2)


def embedding_distance(
    embedding1: npt.NDArray[np.float32], embedding2: npt.NDArray[np.float32]
) -> npt.NDArray[np.float32]:
    return euclidean_distances(embedding1, embedding2)

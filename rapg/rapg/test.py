import torch
from transformers import DistilBertTokenizer, DistilBertForMaskedLM
from .model import load_model
from .prompts import load_prompts
from .data.monsters import load_all_monsters
import numpy as np
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from .similarity import test_similarity


def test_predictions():
    model, tokenizer = load_model()
    prompts = load_prompts()

    for prompt in prompts:
        answer = masked_prediction(model, tokenizer, prompt.prompt)
        print(f"Prompt: {prompt.prompt}")
        print(f"Answer: {answer}")
        print(f"Expected: {prompt.answer}")


def masked_prediction(
    model: DistilBertForMaskedLM, tokenizer: DistilBertTokenizer, prompt: str
) -> str:
    # Tokenize the input
    inputs = tokenizer(prompt, return_tensors="pt")
    mask_token_index = torch.where(inputs["input_ids"] == tokenizer.mask_token_id)[1]

    # Check if GPU is available
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # Move inputs to the GPU if available
    inputs = {key: value.to(device) for key, value in inputs.items()}

    # Generate predictions using the fine-tuned model
    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        mask_token_logits = logits[0, mask_token_index, :]
        predicted_token_id = torch.argmax(mask_token_logits, dim=-1)
        predicted_word = tokenizer.decode(predicted_token_id)

    return predicted_word


def cluster_creatures():
    monsters = load_all_monsters()
    model, tokenizer = load_model()

    # Check if GPU is available
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    vectors = []
    for monster in monsters:
        # Tokenize the text
        inputs = tokenizer(
            text=f"<MonsterName>{monster.name}</MonsterName>", return_tensors="pt"
        )

        # Move inputs to the GPU if available
        inputs = {key: value.to(device) for key, value in inputs.items()}

        # Generate embeddings using the model
        with torch.no_grad():
            outputs = model(**inputs, output_hidden_states=True)
            embeddings = outputs.hidden_states[-1]

        # Aggregate embeddings (e.g., by taking the mean)
        vector = embeddings.mean(dim=1).squeeze().cpu().numpy()
        vectors.append(vector)

    vectors = np.asarray(vectors)

    n_clusters = 12
    clf = KMeans(n_clusters=n_clusters)
    cluster_indexes = clf.fit_predict(vectors)

    cluster_names = []
    for cluster_index in range(n_clusters):
        center = clf.cluster_centers_[cluster_index, :]
        vector_index = find_closest_vector(center, vectors)
        count = np.sum(cluster_indexes == cluster_index)
        cluster_name = f"{monsters[vector_index].name} ({count})"
        cluster_names.append(cluster_name)
    cluster_names = np.asarray(cluster_names, dtype=str)
    cluster_labels = cluster_names[cluster_indexes]

    pca = PCA(n_components=2)
    X_new = pca.fit_transform(vectors)

    cluster_centers_new = pca.transform(clf.cluster_centers_)

    df = pd.DataFrame(
        [
            pd.Series(X_new[:, 0], name="pca1"),
            pd.Series(X_new[:, 1], name="pca2"),
            pd.Series(cluster_labels, name="cluster"),
        ]
    ).T

    fig, (ax) = plt.subplots(1, 1, figsize=(16, 9))
    sns.kdeplot(
        data=df,
        x="pca1",
        y="pca2",
        hue="cluster",
        levels=20,
        ax=ax,
        fill=True,
        alpha=0.5,
    )
    ax.scatter(
        x=cluster_centers_new[:, 0],
        y=cluster_centers_new[:, 1],
        marker="x",
    )
    plt.show(block=True)


def find_closest_vector(cluster_center: np.ndarray, vectors: np.ndarray) -> int:
    distances = np.linalg.norm(vectors - cluster_center, axis=1)
    closest_index = np.argmin(distances)
    return closest_index


def main():
    test_similarity()


if __name__ == "__main__":
    # cluster_creatures()
    main()

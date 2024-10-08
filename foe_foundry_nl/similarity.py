# from ..rapg.rapg.data.datasets import load_5e_srd_monster_descriptions
# from transformers import DistilBertTokenizer, DistilBertForMaskedLM
# from transformers import BatchEncoding
# from sklearn.metrics.pairwise import cosine_similarity
# import numpy as np
# import torch
# import pandas as pd
# from collections.abc import Iterable

# from .model import load_model
# import seaborn as sns
# import matplotlib.pyplot as plt


# def _tokenize(tokenizer: DistilBertTokenizer, text: str) -> BatchEncoding:
#     # Check if GPU is available
#     device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

#     inputs = tokenizer(text=text, return_tensors="pt")
#     inputs = {key: value.to(device) for key, value in inputs.items()}
#     return inputs


# def _embed(model: DistilBertForMaskedLM, inputs: BatchEncoding) -> np.array:
#     with torch.no_grad():
#         outputs = model(**inputs, output_hidden_states=True)
#         embedding = outputs.hidden_states[-1]

#     return embedding.mean(dim=1).squeeze().cpu().numpy()


# def iter_test_data() -> Iterable[tuple[str, str]]:
#     descriptions = load_5e_srd_monster_descriptions()

#     for item in descriptions:
#         name: str = item["name"]
#         description: str = item["text"]

#         index = description.index("</MonsterName>")
#         clean_description = description[index:]

#         clean_description = clean_description.replace(name, "it")
#         yield clean_description, name


# def measure_similarity(
#     model: DistilBertForMaskedLM, tokenizer: DistilBertTokenizer, text1: str, text2: str
# ) -> float:
#     # tokenize text
#     inputs1 = _tokenize(tokenizer, text1)
#     inputs2 = _tokenize(tokenizer, text2)

#     embedding1 = _embed(model, inputs1)
#     embedding2 = _embed(model, inputs2)

#     similarity = cosine_similarity(embedding1[np.newaxis, :], embedding2[np.newaxis, :])
#     return similarity.item()


# def test_similarity():
#     model, tokenizer = load_model()

#     similarities = []
#     for description, answer in iter_test_data():
#         similarity = measure_similarity(model, tokenizer, description, answer)
#         similarities.append(similarity)

#     _, ax = plt.subplots(1, 1, figsize=(16, 9))
#     data = pd.DataFrame([pd.Series(similarities, name="Similarity")]).T
#     sns.histplot(data=data, x="Similarity", ax=ax)
#     plt.show(block=True)

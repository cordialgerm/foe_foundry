

## Goals

- Want to allow user to search for **Monsters** and **Powers** using free-text
- Ex: "A scary ice-monster" should return the **Yeti** Monster from the SRD, and should have high similarity with monstrous, fear-based, and cold Powers


## Design Considerations Notes

- Want to learn more about LLMs so implement things myself using open source tools
- Can use openAI's embeddings to "bootstrap" the training process
- Embeddings for similarity search will be calculated locally using the open source model
- Should be able to fine tune model on general D&D background knowledge as well as specific monster data
- Use masked token prediction for fine tuning based on general knowledge
- Use contrastive learning of positive and negative pairs of monsters, powers, and queries to fine-tune the model

## Implementation Plan

- Generate OpenAI Embeddings for monsters and powers
  - Use OpenAI’s `text-embedding-ada-002` model to generate embeddings for both monsters and powers.
  - Use `openai.Embedding.create()`
  - Store the embeddings for later use in similarity analysis and contrastive learning fine-tuning.
- Identify Monster-Power Relationships (positive pairs and negative pairs) using cosine similarity:
  - Use cosine similarity to calculate similarity scores between monster embeddings and power embeddings.
  - Positive pairs: Monster-power pairs with high cosine similarity (e.g., similarity score ≥ 0.8).
  - Negative pairs: Monster-power pairs with low cosine similarity (e.g., similarity score ≤ 0.4).
  - Use `sklearn.metrics.pairwise.cosine_similarity()` to compute cosine similarity between embeddings.
- Use a local model (`SentenceTransformer`)
  - The local model will be based on Hugging Face’s `SentenceTransformer` for fine-tuning on both monster-power relationships and background knowledge.
  - Example model: `SentenceTransformer('bert-base-uncased')`
- Fine-Tune on Background Knowledge using MLM for domain specialization
  - Fine-tune on the background D&D and RPG markdown content using Masked Language Modeling (MLM) to help the model become more familiar with domain-specific language, rules, and terminology.
  - Python methods:
    - Use `BertForMaskedLM` from `transformers` for MLM fine-tuning.
    - Use `Trainer` from `transformers` with `DataCollatorForLanguageModeling` to train the model on masked tokens in the corpus.
    - Optionally, use Next Sentence Prediction (NSP) with `BertForNextSentencePrediction` for logical sentence flow training.
 - Fine-Tune the Local Model using contrastive learning on monster-power pairs:
  - Objective: Fine-tune the model using contrastive learning to bring related monster-power pairs closer together and push unrelated pairs farther apart in the embedding space.
  - Python methods:
    - Use `InputExample` from `sentence_transformers` to structure training data as pairs.
    - Use `MultipleNegativesRankingLoss()` from `sentence_transformers.losses` to implement contrastive learning for entity matching.
    - Use `model.fit()` from `sentence_transformers` to fine-tune the model on monster-power pairs.
- Use fine-tuned model for local real-time similarity search and query handling:
  - Once fine-tuned, the SentenceTransformer model can be used for local inference without calling the OpenAI API.
  - Python methods:
    - `model.encode()`: Generate embeddings for new queries (monsters or powers) using the fine-tuned model.
    - Use `cosine_similarity()` from `sklearn.metrics.pairwise` to compute similarity between the query embeddings and existing database embeddings (monsters/powers).


## Contrastive Learning

### Monster ↔ Monster

- Help model understand which monsters are similar to one another based on their traits, abilities, and descriptions.
- Contrastive Objective: Bring similar monsters closer together in the embedding space (e.g., dragons with fire breath) and push dissimilar monsters apart (e.g., a fire-breathing dragon and an ice elemental).

### Power ↔ Power

- Capture the similarity between different powers, especially when powers have overlapping themes (e.g., multiple fire-based attacks or defensive powers).
- Contrastive Objective: Bring related powers closer in the embedding space (e.g., fireball and flame strike) and push unrelated powers apart (e.g., healing spell vs. offensive power).

### Monster ↔ Power

- Learn the relationship between specific monsters and the powers that might be relevant to them, allowing the model to recommend powers that fit certain monsters and vice versa.
- Contrastive Objective: Bring related monster-power pairs closer together (e.g., a fire-breathing dragon with fire-related powers) and push unrelated pairs apart (e.g., a frost elemental with fire-based powers).

### Input Text <-> Monsters, Powers

- Learn relationship between specific input texts and monsters or powers
- Can use descriptions taken from the monsters themselves to generate training pairs
- Will help the model generalize the embedding space to user queries
- Include different levels of abstraction (e.g., very specific monster descriptions as well as broader thematic keywords)

### Contrastive Learning Across Pairs:

Use the MultipleNegativesRankingLoss or similar contrastive learning methods from the `sentence-transformers` library to fine-tune the model on these pairs. This will allow the model to optimize its embedding space across combinations of queries, monsters, and powers. Will create a robust embedding space that will allow for flexible similarity searches and queries across both entities.

## Query Classification

- Create a classifier to classify user queries as being either related to a Monster or a Power
- Train on sample corpus of random text (negative examples)
- Train on sample corpus of monster descriptions and summaries
- This will allow detection of real queries vs garbage queries

## Query Expansion

- Supplement user input with synonyms or related terms to improve search results
- Use TF-IDF and/or attention weights to identify which words are important
- Look for descriptive words taht have meaning about monster's powers, traits, or abilities
- Look for action-oriented words that imply what the monster can do
- Look for Nouns and Adjectives. Verbs might not be as helpful
- Enrich the original embedded query with the weighted average of the expanded query terms
- Some things to consider
  - Creature Type
  - Monster Role
  - Challenge Rating
  - Damage Types
  - Weapon Attacks
  - Adjectives
  - Nouns
  - Related SRD Monsters

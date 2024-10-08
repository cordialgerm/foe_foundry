import spacy

# Load the spaCy English model
nlp = spacy.load("en_core_web_lg")

# Define the text and keywords
text = "scary undead monster that drains the life from its enemies"
keywords = [
    "undead",
    "celestial",
    "fiend",
    "holy",
    "curse",
    "ghost",
    "death",
    "necrotic",
    "fearsome",
]

# English pipelines include a rule-based lemmatizer
lemmatizer = nlp.get_pipe("lemmatizer")

text_doc = nlp(text)


# Calculate the similarity score for each keyword
scores = {}
matches = []
for keyword in keywords:
    keyword_doc = nlp(keyword)

    for token in keyword_doc:
        print(token.text, token.has_vector, token.vector_norm, token.is_oov)

    for chunk in text_doc.noun_chunks:
        s = keyword_doc.similarity(chunk)
        if s > 0.5:
            matches.append({"keyword": keyword, "chunk": chunk, "score": s})

    similarity_score = keyword_doc.similarity(text_doc)
    scores[keyword] = similarity_score

# Print the scores
print("text: ", text)
print("lemmized: ", text_doc)
print("chunks...")
for chunk in text_doc.noun_chunks:
    print(chunk)

for match in matches:
    print(f"Keyword: {match['keyword']}, Chunk: {match['chunk']}, Score: {match['score']}")

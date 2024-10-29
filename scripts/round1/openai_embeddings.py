import os
from pathlib import Path

from openai import OpenAI

# buffer = base64.b64decode(base64_encoded)
# base64_embedding = np.frombuffer(buffer, dtype=np.float32)
# base64_embedding


def main():
    client = OpenAI(api_key=os.environ.get("oai"))

    monster_dir = Path(__file__).parent.parent / "data" / "5e_canonical"
    embedding_dir = Path(__file__).parent.parent / "data" / "5e_canonical_embeddings"
    embedding_dir.mkdir(exist_ok=True, parents=True)

    for monster_path in monster_dir.rglob("*.md"):
        monster_md = monster_path.read_text(encoding="utf-8")
        embedding_path = embedding_dir / f"{monster_path.stem}.txt"
        if embedding_path.exists():
            continue

        print(f"Getting embedding for {embedding_path.stem}...")
        embedding = get_embedding(client, monster_md)
        embedding_path.write_text(embedding, encoding="utf-8")


def get_embedding(client: OpenAI, text: str) -> str:
    embedding = client.embeddings.create(
        input=text, encoding_format="base64", model="text-embedding-3-small"
    )
    return embedding.data[0].embedding  # type: ignore -- this is a str


if __name__ == "__main__":
    main()

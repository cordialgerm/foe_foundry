import requests
from pathlib import Path
import time
import numpy as np


def load_articles():
    article_dir = Path(__file__).parent / "raw"

    loaded_ids = np.array(
        [int(f.stem.split("post-")[1]) for f in article_dir.glob("*.html")]
    )
    start_id = int(np.max(loaded_ids)) + 1

    max_post_id = 5687
    downloads = 0
    for id in np.arange(start_id, max_post_id):
        time.sleep(0.1)
        article_url = f"https://www.themonstersknow.com/?p={id}"
        response = requests.get(article_url)
        if response.status_code == 200:
            article_path = article_dir / f"post-{id}.html"
            if article_path.exists():
                continue

            with article_path.open("w", encoding="utf-8") as file:
                file.write(response.text)
                print(f"Downloaded {article_url}")
                downloads += 1

    print(f"Downloaded {downloads} articles")


if __name__ == "__main__":
    load_articles()

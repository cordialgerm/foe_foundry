import time
from pathlib import Path

import numpy as np
import requests
from bs4 import BeautifulSoup


def load_articles():
    article_dir = Path.cwd() / "cache" / "the_monsters_know"
    article_dir.mkdir(exist_ok=True, parents=True)

    loaded_ids1 = [int(f.stem.split("post-")[1]) for f in article_dir.glob("*.html")]
    loaded_ids2 = [
        int(f.stem.split("post-")[1])
        for f in (Path.cwd() / "data" / "the_monsters_know").glob("*.md")
    ]
    loaded_ids = list(set(loaded_ids1 + loaded_ids2))
    start_id = int(np.max(loaded_ids)) + 1

    max_post_id = 6362
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


def transform():
    parent_dir = Path(__file__).parent
    raw_dir = parent_dir / "raw"
    transformed_dir = Path(__file__).parent / "transformed"
    transformed_dir.mkdir(exist_ok=True)

    for article_path in raw_dir.glob("*.html"):
        try:
            html_content = article_path.read_text(encoding="utf-8")
            if "<html" not in html_content.lower():
                continue

            soup = BeautifulSoup(html_content, "html.parser")

            # article title
            title = soup.find("h2")
            title_text = title.get_text()

            # Extract the article content
            article = soup.find("div", class_="entry-content")
            article_text = article.get_text()

            clean_path = transformed_dir / f"{article_path.stem}.md"

            md = f"## {title_text}\n\n{article_text}"
            clean_path.write_text(md, encoding="utf-8")
            print(
                f"Transformed {article_path.relative_to(parent_dir)} to {clean_path.relative_to(parent_dir)}"
            )
        except Exception as x:
            print(f"Unable to transform {article_path.relative_to(parent_dir)}. {x}")


if __name__ == "__main__":
    load_articles()
    transform()

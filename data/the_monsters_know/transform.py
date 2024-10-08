from pathlib import Path
from bs4 import BeautifulSoup


def main():
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
    main()

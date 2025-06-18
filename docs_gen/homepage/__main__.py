from pathlib import Path

from .gen_homepage import generate_homepage

if __name__ == "__main__":
    site_dir = Path.cwd() / "site"
    site_dir.mkdir(exist_ok=True)
    output_path = site_dir / "index.html"
    generate_homepage(output_path)
    print(f"Homepage generated at {output_path.resolve()}")

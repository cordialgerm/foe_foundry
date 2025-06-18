import os
import re
from pathlib import Path

import jinja2
from markupsafe import Markup
from mkdocs.config import load_config
from mkdocs.config.config_options import ExtraScriptValue
from mkdocs.structure.files import get_files
from mkdocs.structure.nav import get_navigation
from mkdocs.utils import normalize_url

from foe_foundry_data.homepage import load_homepage_data
from foe_foundry_data.markdown import create_newsletter

BASE_URL = "http://localhost:8000/"


def _url_filter(path: str) -> str:
    return normalize_url(path, base=BASE_URL)


def _script_tag_filter(extra_script: ExtraScriptValue) -> str:
    """Converts an ExtraScript value to an HTML <script> tag line."""
    html = '<script src="{0}"'
    if not isinstance(extra_script, str):
        if extra_script.type:
            html += ' type="{1.type}"'
        if extra_script.defer:
            html += " defer"
        if extra_script.async_:
            html += " async"
    html += "></script>"
    return Markup(html).format(_url_filter(str(extra_script)), extra_script)


def _find_minified_version(
    source_name: str, source_ext: str, search_dir: Path, relative_to: Path
) -> str:
    # Match files like:
    # - site.css
    # - site.min.css
    # - site.123abc.css
    # - site.123abc.min.css
    pattern = re.compile(
        rf"^{re.escape(source_name)}(?:\.[\w\d]+)?(?:\.min)?{re.escape(source_ext)}$"
    )

    matches = []
    for path in Path(search_dir).rglob(f"{source_name}*{source_ext}"):
        if pattern.match(path.name):
            matches.append(path)

    if len(matches) == 0:
        raise FileNotFoundError(
            f"No minified version of {source_name} found in {search_dir}"
        )

    match = matches[0]
    rel_path = match.relative_to(relative_to)
    return str(rel_path)


def generate_homepage(output_path: Path):
    if os.environ.get("SITE_URL") is None:
        os.environ.setdefault("SITE_URL", BASE_URL)

    data = load_homepage_data()

    # Set up Jinja
    template_dir = Path(__file__).parent.parent.parent / "docs_theme"
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir))

    # Register the filter
    env.filters["url"] = _url_filter
    env.filters["script_tag"] = _script_tag_filter
    env.globals["render_newsletter"] = create_newsletter

    # Now render as normal
    template = env.get_template("base.html")

    config = load_config("mkdocs.yml")
    files = get_files(config)
    nav = get_navigation(files, config)

    # minification plugin messes things up
    config.extra_css = [
        _find_minified_version(
            "site", ".css", Path.cwd() / "site" / "css", Path.cwd() / "site"
        )
    ]
    config.extra_javascript = [  # type: ignore
        _find_minified_version(
            "extras", ".js", Path.cwd() / "site" / "scripts", Path.cwd() / "site"
        )
    ]

    page = {
        "base_url": BASE_URL,
        "is_homepage": True,
        "canonical_url": "localhost:8000",
        "title": "Homepage Mockup",
        "description": "A mockup of the homepage for Foe Foundry",
        "meta": {"image": "img/icons/favicon.webp"},
    }

    rendered = template.render(homepage_data=data, config=config, page=page, nav=nav)
    output_path.write_text(rendered)

from foe_foundry.statblocks import Statblock

from .data import StatblockJinjaContext
from .env import JinjaEnv


def render_statblock_fragment(stats: Statblock) -> str:
    """Renders a statblock HTML fragment for a single statblock"""

    template = JinjaEnv.get_template("statblock.html.j2")
    data = StatblockJinjaContext.from_statblock(stats)
    context = dict(statblock=data.to_dict())
    html_raw = template.render(context)
    return html_raw


def render_statblock_markdown(stats: Statblock, format: str = "5esrd") -> str:
    """Renders a statblock as markdown for the specified format
    
    Args:
        stats: The Statblock object to render
        format: One of "5esrd", "gmbinder", "homebrewery", "blackflag"
    
    Returns:
        Markdown string representation of the statblock
    """
    
    # Map format to template file
    format_templates = {
        "5esrd": "statblock-5esrd.md.j2",
        "gmbinder": "statblock-gmbinder.md.j2", 
        "homebrewery": "statblock-homebrewery.md.j2",
        "blackflag": "statblock-blackflag.md.j2"
    }
    
    if format not in format_templates:
        raise ValueError(f"Unknown format '{format}'. Supported formats: {list(format_templates.keys())}")
    
    template_name = format_templates[format]
    template = JinjaEnv.get_template(template_name)
    data = StatblockJinjaContext.from_statblock(stats)
    context = dict(statblock=data.to_dict())
    markdown_raw = template.render(context)
    return markdown_raw

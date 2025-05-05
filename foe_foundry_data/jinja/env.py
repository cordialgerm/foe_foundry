from functools import partial

from .utilities import (
    branding,
    columns,
    fix_punctuation,
    jinja_env,
    markdown_no_wrapping_p,
)

JinjaEnv = jinja_env()
JinjaEnv.filters["fix_punctuation"] = fix_punctuation
JinjaEnv.filters["markdown_no_wrapping_p"] = markdown_no_wrapping_p
JinjaEnv.globals["columns"] = columns
JinjaEnv.globals["branding"] = partial(branding, JinjaEnv)

import os


def get_base_url() -> str:
    """Returns the base URL for the site, ensuring it does not end with a slash."""

    base_url = os.environ.get("SITE_URL")
    if base_url is None:
        raise ValueError("SITE_URL environment variable is not set.")
    if base_url.endswith("/"):
        base_url = base_url[:-1]

    return base_url

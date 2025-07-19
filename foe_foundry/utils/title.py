def slug_to_title(slug: str) -> str:
    """Convert a slug to a title by replacing hyphens and underscores with spaces and capitalizing each word"""
    return slug.replace("-", " ").replace("_", " ").title()

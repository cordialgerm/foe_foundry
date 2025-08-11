def name_to_key(name: str) -> str:
    return (
        name.lower()
        .strip()
        .replace(" ", "-")
        .replace("_", "-")
        .replace("/", "-")
        .replace("'", "")
        .replace("(", "")
        .replace(")", "")
    )

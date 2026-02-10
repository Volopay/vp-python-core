def to_camel(snake_str: str) -> str:
    parts = snake_str.split("_")
    return parts[0] + "".join(
        p.upper() if p.lower() == "id" else p.title() for p in parts[1:]
    )

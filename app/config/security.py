import re

def sanitize_query(query: str) -> str:
    """
    Sanitizes user queries to strip potentially malicious characters
    or prompt injection structures while retaining alphanumeric phrases.
    """
    if not query:
        return ""
    # Keep alphanumeric characters, spaces, and basic mathematical or punctuation symbols
    sanitized = re.sub(r"[^\w\s\?\.\!\-\:\(\)\,\*\/\+]", "", query)
    return sanitized.strip()

def validate_query_length(query: str, max_length: int = 2000) -> bool:
    """
    Ensures query inputs conform to length thresholds.
    """
    return len(query) <= max_length

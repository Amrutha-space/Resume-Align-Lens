"""
CVAlign Lens — Text Processing Utilities
Clean, normalize, and prepare text before feeding to the LLM.
"""

import re
import unicodedata


def clean_text(text: str) -> str:
    """
    Normalize and clean raw text input.
    Removes excessive whitespace, normalizes unicode, strips control characters.
    """
    if not text:
        return ""

    # Normalize unicode characters
    text = unicodedata.normalize("NFKD", text)

    # Remove non-printable characters except standard whitespace
    text = re.sub(r"[^\x20-\x7E\n\t]", " ", text)

    # Normalize line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Collapse excessive blank lines (more than 2 in a row)
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Collapse excessive spaces within lines
    lines = [re.sub(r" {2,}", " ", line) for line in text.split("\n")]
    text = "\n".join(lines)

    return text.strip()


def truncate_text(text: str, max_chars: int = 8000) -> str:
    """
    Safely truncate text to a maximum character limit.
    Truncates at the nearest sentence boundary if possible.
    """
    if len(text) <= max_chars:
        return text

    truncated = text[:max_chars]
    last_period = truncated.rfind(".")
    if last_period > max_chars * 0.8:
        return truncated[:last_period + 1]
    return truncated


def is_meaningful_text(text: str, min_words: int = 30) -> bool:
    """
    Validate that the provided text has enough substance to analyze.
    """
    if not text:
        return False
    word_count = len(text.split())
    return word_count >= min_words


def sanitize_json_string(value: str) -> str:
    """
    Escape characters that could break JSON serialization.
    """
    if not isinstance(value, str):
        return str(value)
    return value.replace("\\", "\\\\").replace('"', '\\"')

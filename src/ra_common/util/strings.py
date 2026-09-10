"""Small string helpers. Ports ``ra.common.StringUtil``."""

from __future__ import annotations


def capitalize_first(text: str) -> str:
    """Uppercase the first character, leave the rest untouched."""
    if not text:
        return ""
    return text[0].upper() + text[1:]


def capitalize(text: str) -> str:
    """Uppercase the first character and every character following a space."""
    out: list[str] = []
    capitalize_next = True
    for ch in text:
        if capitalize_next and ch != " ":
            out.append(ch.upper())
            capitalize_next = False
        else:
            out.append(ch)
            capitalize_next = ch == " "
    return "".join(out)

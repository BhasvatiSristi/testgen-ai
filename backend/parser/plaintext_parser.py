"""Plain-English input parser for the TestGen AI agent."""

from __future__ import annotations


def parse_plaintext(content: str) -> dict:
    """Wrap raw plain-English requirements in a normalized dict."""

    return {"raw_description": content, "type": "plaintext"}

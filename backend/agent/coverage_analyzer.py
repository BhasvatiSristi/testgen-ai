"""Coverage analysis for generated tests."""

from __future__ import annotations

import re
from typing import Any


def _collect_generated_text(generated_tests: dict) -> str:
    if not isinstance(generated_tests, dict):
        return ""

    chunks: list[str] = []
    for value in generated_tests.values():
        if isinstance(value, str):
            chunks.append(value)
        elif value is not None:
            chunks.append(str(value))
    return "\n".join(chunks).lower()


def _endpoint_label(endpoint: dict) -> str:
    method = str(endpoint.get("method", "") or "").strip().upper()
    path = str(endpoint.get("path", "") or "").strip()
    if method and path:
        return f"{method} {path}"
    return path or method or "unknown endpoint"


def _endpoint_is_covered(search_text: str, endpoint: dict) -> bool:
    path = str(endpoint.get("path", "") or "").strip().lower()
    if not path:
        return False

    if path in search_text:
        return True

    def _replace_path_parameter(match: re.Match[str]) -> str:
        return r"[^\"'`\s/]+"

    escaped_path = re.escape(path)
    escaped_path = re.sub(r"\\\{[^\\}]+\\\}", _replace_path_parameter, escaped_path)
    pattern = re.compile(escaped_path, re.IGNORECASE)
    return bool(pattern.search(search_text))


def analyze_coverage(parsed_input: dict, generated_tests: dict) -> dict:
    """Estimate endpoint coverage from generated test code strings."""

    endpoints = parsed_input.get("endpoints") if isinstance(parsed_input, dict) else []
    normalized_endpoints = [endpoint for endpoint in endpoints if isinstance(endpoint, dict)] if isinstance(endpoints, list) else []
    search_text = _collect_generated_text(generated_tests)

    covered_endpoints: list[str] = []
    uncovered_endpoints: list[str] = []

    for endpoint in normalized_endpoints:
        label = _endpoint_label(endpoint)
        if _endpoint_is_covered(search_text, endpoint):
            covered_endpoints.append(label)
        else:
            uncovered_endpoints.append(label)

    total_endpoints = len(normalized_endpoints)
    covered = len(covered_endpoints)
    coverage_pct = round((covered / total_endpoints) * 100) if total_endpoints else 0

    return {
        "total_endpoints": total_endpoints,
        "covered": covered,
        "uncovered": uncovered_endpoints,
        "coverage_pct": coverage_pct,
    }
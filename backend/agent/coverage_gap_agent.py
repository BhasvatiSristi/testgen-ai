"""Suggest missing test scenarios from the existing generated tests."""

from __future__ import annotations

import json
import re
from typing import Any

from mistralai.client import Mistral

from backend.config import MAX_TOKENS, MISTRAL_API_KEY, MODEL

PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}


def _get_client() -> Mistral:
    if not MISTRAL_API_KEY:
        raise ValueError("MISTRAL_API_KEY is not configured. Set it in the .env file.")
    return Mistral(api_key=MISTRAL_API_KEY)


def _chat(client: Mistral, messages: list[dict]) -> str:
    response = client.chat.complete(
        model=MODEL,
        messages=messages,
        temperature=0.2,
        max_tokens=MAX_TOKENS,
        response_format={"type": "json_object"},
    )
    content = ""
    if getattr(response, "choices", None):
        first_choice = response.choices[0]
        message = getattr(first_choice, "message", None)
        content = getattr(message, "content", "") or ""
    return content.strip()


def _strip_code_fences(text: str) -> str:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\s*```$", "", cleaned)
    return cleaned.strip()


def _extract_json(text: str) -> Any:
    cleaned = _strip_code_fences(text)
    try:
        return json.loads(cleaned)
    except Exception:
        match = re.search(r"\[.*\]", cleaned, flags=re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except Exception:
                return []
    return []


def _normalize_priority(value: str) -> str:
    normalized = (value or "").strip().lower()
    if normalized not in PRIORITY_ORDER:
        return "medium"
    return normalized


def suggest_missing_tests(parsed_input: dict, existing_tests: dict) -> list[dict]:
    """Ask Mistral which test scenarios are still missing."""

    client = _get_client()
    payload = {
        "endpoints": parsed_input.get("endpoints", []) if isinstance(parsed_input, dict) else [],
        "existing_tests": existing_tests or {},
    }
    prompt = (
        "Given these endpoints and the existing tests, which test scenarios are MISSING?\n"
        "Return ONLY valid JSON as an array of objects. Each object must have keys: endpoint, missing_scenario, priority.\n"
        "Use priority values high, medium, or low.\n\n"
        f"Input:\n{json.dumps(payload, indent=2, sort_keys=True)}"
    )
    response_text = _chat(
        client,
        [
            {"role": "system", "content": "You are a senior QA analyst focused on test gap analysis."},
            {"role": "user", "content": prompt},
        ],
    )
    parsed = _extract_json(response_text)
    if not isinstance(parsed, list):
        return []

    normalized: list[dict] = []
    for item in parsed:
        if not isinstance(item, dict):
            continue
        endpoint = str(item.get("endpoint", "") or "").strip()
        missing_scenario = str(item.get("missing_scenario", "") or "").strip()
        priority = _normalize_priority(str(item.get("priority", "") or ""))
        if endpoint and missing_scenario:
            normalized.append(
                {
                    "endpoint": endpoint,
                    "missing_scenario": missing_scenario,
                    "priority": priority,
                }
            )

    normalized.sort(key=lambda gap: PRIORITY_ORDER.get(gap["priority"], 1))
    return normalized

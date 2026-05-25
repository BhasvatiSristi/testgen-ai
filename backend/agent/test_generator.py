"""Two-shot Mistral pipeline for test generation."""

from __future__ import annotations

import json
import re
from typing import Any

try:
    from mistralai.client import Mistral
    HAS_MISTRAL = True
except Exception:
    Mistral = None  # type: ignore
    HAS_MISTRAL = False

from backend.config import MAX_TOKENS, MISTRAL_API_KEY, MODEL

JSON_MODE = {"type": "json_object"}

EXTRACTION_SYSTEM_PROMPT = (
    "You are a QA architect. Analyze the following API spec or description and "
    "extract all testable components. Return ONLY valid JSON with no extra text, "
    "no markdown fences."
)

EXTRACTION_USER_TEMPLATE = (
    "Extract from this spec:\n"
    "{context}\n\n"
    "Return JSON with keys: functions, endpoints, edge_cases, data_types, auth_requirements"
)

PYTEST_PROMPT = """You are generating production-quality pytest suites from structured API analysis.

Return ONLY a JSON object with these exact keys: unit, integration, edge_cases.
Each value must be a string containing Python test code.

Generate UNIT tests covering: happy path, invalid inputs, missing required fields.
Generate INTEGRATION tests covering: full request/response cycle, status codes, response schema.
Generate EDGE CASE tests covering: empty strings, null values, boundary numbers, SQL injection strings, very long inputs, unicode characters.

Add a comment above each test explaining WHAT it tests and WHY.

Use pytest classes where it improves organization, prefer fixtures and parametrize decorators for repeated scenarios, and include conftest.py fixture suggestions as commented snippets when helpful.
Use clear assertions, deterministic data, and code that can run without markdown fences or narrative text.

Extracted JSON:
{analysis_json}
"""

JEST_PROMPT = """You are generating production-quality Jest suites from structured API analysis.

Return ONLY a JSON object with these exact keys: unit, integration, edge_cases.
Each value must be a string containing JavaScript or TypeScript test code.

Generate UNIT tests covering: happy path, invalid inputs, missing required fields.
Generate INTEGRATION tests covering: full request/response cycle, status codes, response schema.
Generate EDGE CASE tests covering: empty strings, null values, boundary numbers, SQL injection strings, very long inputs, unicode characters.

Add a comment above each test explaining WHAT it tests and WHY.

Use describe/it blocks, beforeEach where setup is needed, expect().toBe() and related matchers, and mock imports for dependencies.
Prefer focused assertions, stable test data, and output that can be pasted directly into a Jest test file.

Extracted JSON:
{analysis_json}
"""

JUNIT_PROMPT = """You are generating production-quality JUnit 5 suites from structured API analysis.

Return ONLY a JSON object with these exact keys: unit, integration, edge_cases.
Each value must be a string containing Java test code for JUnit 5.

Generate UNIT tests covering: happy path, invalid inputs, missing required fields.
Generate INTEGRATION tests covering: full request/response cycle, status codes, response schema.
Generate EDGE CASE tests covering: empty strings, null values, boundary numbers, SQL injection strings, very long inputs, unicode characters.

Add a comment above each test explaining WHAT it tests and WHY.

Use a JUnit 5 test class, @Test annotated methods, and clear assertions. Add @BeforeEach when setup is helpful, keep the code deterministic, and make the output ready to paste into a Java test file.

Extracted JSON:
{analysis_json}
"""

FRAMEWORK_PROMPTS = {
    "pytest": PYTEST_PROMPT,
    "jest": JEST_PROMPT,
    "junit": JUNIT_PROMPT,
    "rspec": """You are generating production-quality RSpec suites from structured API analysis.

Return ONLY a JSON object with these exact keys: unit, integration, edge_cases.
Each value must be a string containing Ruby test code.

Generate UNIT tests covering: happy path, invalid inputs, missing required fields.
Generate INTEGRATION tests covering: full request/response cycle, status codes, response schema.
Generate EDGE CASE tests covering: empty strings, null values, boundary numbers, SQL injection strings, very long inputs, unicode characters.

Add a comment above each test explaining WHAT it tests and WHY.

Use describe blocks, it examples, before hooks, let/let!, and readable expectations. Keep the output ready to paste into an RSpec file.

Extracted JSON:
{analysis_json}
""",
}

SECTION_LABELS = {
    "unit": "UNIT",
    "integration": "INTEGRATION",
    "edge_cases": "EDGE CASE",
}


def _get_client() -> Mistral:
    if not HAS_MISTRAL:
        raise ImportError("mistralai package is not installed in the environment")
    if not MISTRAL_API_KEY:
        raise ValueError("MISTRAL_API_KEY is not configured. Set it in the .env file.")
    return Mistral(api_key=MISTRAL_API_KEY)


def _chat(client: Mistral, messages: list[dict], max_tokens: int = MAX_TOKENS) -> str:
    response = client.chat.complete(
        model=MODEL,
        messages=messages,
        temperature=0.2,
        max_tokens=max_tokens,
        response_format=JSON_MODE,
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


def _extract_json(text: str) -> dict:
    cleaned = _strip_code_fences(text)
    try:
        payload = json.loads(cleaned)
        if isinstance(payload, dict):
            return payload
    except Exception:
        pass

    match = re.search(r"\{.*\}", cleaned, flags=re.DOTALL)
    if match:
        try:
            payload = json.loads(match.group(0))
            if isinstance(payload, dict):
                return payload
        except Exception:
            pass

    return {}


def _default_generation_result() -> dict:
    return {"unit": "", "integration": "", "edge_cases": ""}


def _normalize_generation_payload(payload: Any) -> dict:
    result = _default_generation_result()
    if isinstance(payload, dict):
        for key in result:
            value = payload.get(key, "")
            result[key] = value if isinstance(value, str) else json.dumps(value, indent=2, sort_keys=True)
    return result


def _is_non_empty_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _normalize_framework(framework: str) -> str:
    normalized = (framework or "").strip().lower()
    if normalized in FRAMEWORK_PROMPTS:
        return normalized
    if normalized.startswith("junit"):
        return "junit"
    if normalized.startswith("rspec"):
        return "rspec"
    return "pytest"


def _extract_analysis(context: str, client: Mistral) -> dict:
    extraction_prompt = EXTRACTION_USER_TEMPLATE.format(context=context)
    extraction_text = _chat(
        client,
        [
            {"role": "system", "content": EXTRACTION_SYSTEM_PROMPT},
            {"role": "user", "content": extraction_prompt},
        ],
    )
    extracted_payload = _extract_json(extraction_text)
    if extracted_payload:
        return extracted_payload

    return {
        "functions": [],
        "endpoints": [],
        "edge_cases": [],
        "data_types": {},
        "auth_requirements": [],
        "raw_context": context,
    }


def _section_prompt(framework: str, section: str, analysis_json: str) -> str:
    section_label = SECTION_LABELS[section]
    return f"""You are generating production-quality {framework} tests.

Return ONLY a JSON object with the exact key: {section}.
The value must be a string containing {framework} test code.

Generate {section_label} tests covering:
- happy path
- invalid inputs
- missing required fields
- for edge cases also include empty strings, null values, boundary numbers, SQL injection strings, very long inputs, and unicode characters

Add a comment above each test explaining WHAT it tests and WHY.

If framework is pytest, use pytest classes, fixtures, parametrize decorators, and assert statements. Include conftest.py fixture suggestions as comments when useful.
If framework is jest, use describe/it blocks, beforeEach, expect().toBe(), and mock imports.
If framework is junit, use a JUnit 5 class with @Test methods and clear assertions.

Structured analysis:
{analysis_json}
"""


def _generate_section(client: Mistral, framework: str, section: str, analysis_json: str) -> str:
    section_prompt = _section_prompt(framework, section, analysis_json)
    section_text = _chat(
        client,
        [
            {"role": "system", "content": f"Generate a single {section} test section with no extra text."},
            {"role": "user", "content": section_prompt},
        ],
    )
    section_payload = _extract_json(section_text)
    value = section_payload.get(section, "") if isinstance(section_payload, dict) else ""
    return value if _is_non_empty_text(value) else section_text


def generate_tests(context: str, framework: str = "pytest") -> dict:
    """Run the extraction and generation steps against Mistral."""
    if not HAS_MISTRAL:
        placeholder = {
            "unit": "# Mistral not available in this environment.\n# Set up the MISTRAL_API_KEY secret and install the 'mistralai' package to enable AI-based generation.\n\nimport pytest\n\ndef test_placeholder():\n    \"\"\"Placeholder test: replace with real generated tests after configuring Mistral.\"\"\"\n    assert True\n",
            "integration": "",
            "edge_cases": "",
        }
        return placeholder

    client = _get_client()
    normalized_framework = _normalize_framework(framework)
    extracted_payload = _extract_analysis(context, client)
    analysis_json = json.dumps(extracted_payload, indent=2, sort_keys=True)
    generation_prompt = FRAMEWORK_PROMPTS[normalized_framework].format(analysis_json=analysis_json)

    generation_text = _chat(
        client,
        [
            {"role": "system", "content": "Generate concise, production-ready tests."},
            {"role": "user", "content": generation_prompt},
        ],
    )

    generation_payload = _extract_json(generation_text)
    normalized_result = _normalize_generation_payload(generation_payload)

    for section in normalized_result:
        if not _is_non_empty_text(normalized_result[section]):
            normalized_result[section] = _generate_section(client, normalized_framework, section, analysis_json)

    return normalized_result

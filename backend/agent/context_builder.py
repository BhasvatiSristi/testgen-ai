"""Convert parsed inputs into a prompt-ready context string."""

from __future__ import annotations

import json
from typing import Any, Dict, List


def _format_endpoint(endpoint: dict, index: int) -> str:
    lines = [f"Endpoint {index}"]
    lines.append(f"Path: {endpoint.get('path', '')}")
    lines.append(f"Method: {str(endpoint.get('method', '')).upper()}")

    parameters = endpoint.get("parameters") or []
    lines.append("Parameters:")
    if parameters:
        for parameter in parameters:
            lines.append(
                "- "
                + ", ".join(
                    [
                        f"name={parameter.get('name', '')}",
                        f"in={parameter.get('in', '')}",
                        f"required={parameter.get('required', False)}",
                        f"type={parameter.get('type', '')}",
                        f"description={parameter.get('description', '')}",
                    ]
                )
            )
    else:
        lines.append("- None")

    responses = endpoint.get("responses") or {}
    lines.append("Responses:")
    if responses:
        for status_code, response in responses.items():
            description = response.get("description", "") if isinstance(response, dict) else str(response)
            lines.append(f"- {status_code}: {description}")
    else:
        lines.append("- None")

    return "\n".join(lines)


def build_context(parsed_input: dict) -> str:
    """Return a prompt-ready string for either API specs or plaintext requirements."""

    if not isinstance(parsed_input, dict):
        return ""

    if "raw_description" in parsed_input:
        return str(parsed_input.get("raw_description", "") or "").strip()

    if "endpoints" in parsed_input:
        lines = ["API Specification Summary"]
        lines.append(f"Title: {parsed_input.get('title', '')}")
        lines.append(f"Version: {parsed_input.get('version', '')}")
        lines.append("")

        endpoints = parsed_input.get("endpoints") or []
        for index, endpoint in enumerate(endpoints, start=1):
            if isinstance(endpoint, dict):
                lines.append(_format_endpoint(endpoint, index))
                lines.append("")

        return "\n".join(lines).strip()

    return json.dumps(parsed_input, indent=2, sort_keys=True)

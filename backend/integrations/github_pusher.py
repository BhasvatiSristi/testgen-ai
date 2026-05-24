"""Push generated tests to GitHub using the Contents API."""

from __future__ import annotations

import base64
from typing import Any

import requests


def _path_for_section(section: str) -> str:
    file_names = {
        "unit": "tests/unit_tests.py",
        "integration": "tests/integration_tests.py",
        "edge_cases": "tests/edge_case_tests.py",
    }
    return file_names[section]


def _get_existing_sha(repo: str, path: str, headers: dict[str, str]) -> str:
    url = f"https://api.github.com/repos/{repo}/contents/{path}"
    response = requests.get(url, headers=headers, timeout=30)
    if response.status_code == 200:
        payload = response.json()
        if isinstance(payload, dict):
            return str(payload.get("sha", "") or "")
    return ""


def push_to_github(token: str, repo: str, tests: dict, framework: str) -> dict:
    """Create or update generated test files in a GitHub repository."""

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    urls: list[str] = []
    try:
        for section in ["unit", "integration", "edge_cases"]:
            path = _path_for_section(section)
            content = str((tests or {}).get(section, ""))
            encoded_content = base64.b64encode(content.encode("utf-8")).decode("utf-8")

            payload: dict[str, Any] = {
                "message": f"Add generated {section.replace('_', ' ')} tests",
                "content": encoded_content,
            }
            existing_sha = _get_existing_sha(repo, path, headers)
            if existing_sha:
                payload["sha"] = existing_sha

            url = f"https://api.github.com/repos/{repo}/contents/{path}"
            response = requests.put(url, headers=headers, json=payload, timeout=30)
            if response.status_code not in (200, 201):
                error_message = response.text
                return {"success": False, "urls": urls, "error": error_message}

            result = response.json()
            if isinstance(result, dict):
                html_url = result.get("content", {}).get("html_url") if isinstance(result.get("content"), dict) else None
                if html_url:
                    urls.append(str(html_url))

        return {"success": True, "urls": urls, "error": None}
    except Exception as exc:
        return {"success": False, "urls": urls, "error": str(exc)}
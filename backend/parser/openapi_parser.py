"""Parse OpenAPI or Swagger specifications into a normalized structure."""

from __future__ import annotations

import json
from typing import Any, Dict, List

import yaml

HTTP_METHODS = {"get", "post", "put", "patch", "delete", "options", "head", "trace"}


def _empty_result() -> dict:
    return {"title": "", "version": "", "endpoints": []}


def _load_spec(content: str) -> Any:
    try:
        return json.loads(content)
    except Exception:
        return yaml.safe_load(content)


def _normalize_parameters(parameters: Any) -> List[dict]:
    normalized: List[dict] = []
    if not isinstance(parameters, list):
        return normalized

    for parameter in parameters:
        if not isinstance(parameter, dict):
            continue

        schema = parameter.get("schema")
        schema_type = ""
        if isinstance(schema, dict):
            schema_type = str(schema.get("type", "") or "")
        elif schema is not None:
            schema_type = str(schema)

        normalized.append(
            {
                "name": str(parameter.get("name", "") or ""),
                "in": str(parameter.get("in", "") or ""),
                "required": bool(parameter.get("required", False)),
                "type": schema_type,
                "description": str(parameter.get("description", "") or ""),
            }
        )

    return normalized


def _normalize_responses(responses: Any) -> Dict[str, dict]:
    normalized: Dict[str, dict] = {}
    if not isinstance(responses, dict):
        return normalized

    for status_code, response in responses.items():
        response_data = {"description": "", "content": {}}
        if isinstance(response, dict):
            response_data["description"] = str(response.get("description", "") or "")
            content = response.get("content")
            if isinstance(content, dict):
                for content_type, content_spec in content.items():
                    schema_summary = {}
                    if isinstance(content_spec, dict):
                        schema = content_spec.get("schema")
                        if isinstance(schema, dict):
                            schema_summary = {
                                "type": str(schema.get("type", "") or ""),
                                "format": str(schema.get("format", "") or ""),
                            }
                    response_data["content"][str(content_type)] = schema_summary
        else:
            response_data["description"] = str(response)

        normalized[str(status_code)] = response_data

    return normalized


def parse_openapi(content: str) -> dict:
    """Parse a YAML or JSON OpenAPI document into a clean summary dict."""

    if not isinstance(content, str) or not content.strip():
        return _empty_result()

    try:
        spec = _load_spec(content)
        if not isinstance(spec, dict):
            return _empty_result()

        info = spec.get("info") if isinstance(spec.get("info"), dict) else {}
        title = str(info.get("title", "") or "") if isinstance(info, dict) else ""
        version = str(info.get("version", "") or "") if isinstance(info, dict) else ""

        endpoints: List[dict] = []
        paths = spec.get("paths")
        if isinstance(paths, dict):
            for path, path_item in paths.items():
                if not isinstance(path_item, dict):
                    continue

                shared_parameters = path_item.get("parameters", [])
                for method, operation in path_item.items():
                    if method.lower() not in HTTP_METHODS or not isinstance(operation, dict):
                        continue

                    combined_parameters = []
                    combined_parameters.extend(shared_parameters if isinstance(shared_parameters, list) else [])
                    combined_parameters.extend(operation.get("parameters", []) if isinstance(operation.get("parameters"), list) else [])

                    endpoints.append(
                        {
                            "path": str(path),
                            "method": method.upper(),
                            "parameters": _normalize_parameters(combined_parameters),
                            "responses": _normalize_responses(operation.get("responses", {})),
                        }
                    )

        return {"title": title, "version": version, "endpoints": endpoints}
    except Exception:
        return _empty_result()

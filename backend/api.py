"""HTTP API for the TestGen AI Vue frontend."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from backend.agent.context_builder import build_context
from backend.agent.coverage_analyzer import analyze_coverage
from backend.agent.coverage_gap_agent import suggest_missing_tests
from backend.agent.test_generator import generate_tests
from backend.integrations.github_pusher import push_to_github
from backend.parser.openapi_parser import parse_openapi
from backend.parser.plaintext_parser import parse_plaintext
from backend.storage.history_store import delete_run, get_all_runs, get_run_by_id, save_run

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEMO_DIR = PROJECT_ROOT / "backend" / "demo_examples"
DEPTH_LABELS = {1: "Basic", 2: "Medium", 3: "Deep"}

DEMO_SPECS = {
    "Auth API": {
        "path": DEMO_DIR / "auth_api.yaml",
        "input_type": "OpenAPI / Swagger",
        "description": "Authentication flows, token issuance, and protected routes.",
    },
    "User CRUD": {
        "path": DEMO_DIR / "user_crud.yaml",
        "input_type": "OpenAPI / Swagger",
        "description": "Create, read, update, and delete lifecycle coverage.",
    },
    "Payment flow": {
        "path": DEMO_DIR / "payment_flow.md",
        "input_type": "Plain English",
        "description": "A narrative payment scenario with edge cases.",
    },
}


class GenerateRequest(BaseModel):
    input_type: str = "OpenAPI / Swagger"
    raw_content: str = ""
    framework: str = "pytest"
    test_types: list[str] = Field(default_factory=lambda: ["Unit tests", "Integration tests", "Edge cases"])
    coverage_depth: int = 2
    focus_endpoint: str = ""
    pending_gap_scenario: dict[str, Any] | None = None


class GithubExportRequest(BaseModel):
    repo: str
    token: str
    framework: str = "pytest"
    tests: dict[str, str] = Field(default_factory=dict)


app = FastAPI(title="TestGen AI API", version="2.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _load_demo_content(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8").strip()


def _demo_payload() -> list[dict[str, str]]:
    demos: list[dict[str, str]] = []
    for name, metadata in DEMO_SPECS.items():
        demos.append(
            {
                "name": name,
                "input_type": metadata["input_type"],
                "description": metadata["description"],
                "content": _load_demo_content(metadata["path"]),
            }
        )
    return demos


def _build_generation_context(parsed_input: dict, request: GenerateRequest) -> str:
    context = build_context(parsed_input)
    hints: list[str] = []

    if request.test_types:
        hints.append("Preferred test types:\n- " + "\n- ".join(request.test_types))

    depth_label = DEPTH_LABELS.get(int(request.coverage_depth or 2), "Medium")
    hints.append(f"Coverage depth target: {depth_label}")

    if request.focus_endpoint:
        hints.append(
            "Focus uncovered endpoint: "
            f"{request.focus_endpoint}\n"
            "Generate additional tests that explicitly cover this endpoint."
        )

    gap = request.pending_gap_scenario or {}
    if isinstance(gap, dict):
        endpoint = str(gap.get("endpoint", "") or "").strip()
        missing_scenario = str(gap.get("missing_scenario", "") or "").strip()
        if endpoint or missing_scenario:
            hints.append(
                "Missing scenario: "
                f"{missing_scenario}\n"
                f"Target endpoint: {endpoint}\n"
                "Generate only this missing scenario and keep the response narrowly focused."
            )

    if hints:
        context = f"{context}\n\nGeneration preferences:\n" + "\n\n".join(hints)

    return context


def _parse_input(request: GenerateRequest) -> dict:
    if request.input_type.strip().lower().startswith("openapi"):
        return parse_openapi(request.raw_content)
    return parse_plaintext(request.raw_content)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/demos")
def demos() -> dict[str, list[dict[str, str]]]:
    return {"demos": _demo_payload()}


@app.get("/api/history")
def history() -> dict[str, list[dict]]:
    return {"runs": get_all_runs()}


@app.get("/api/history/{run_id}")
def history_item(run_id: int) -> dict:
    run = get_run_by_id(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return run


@app.delete("/api/history/{run_id}")
def history_delete(run_id: int) -> dict[str, str]:
    delete_run(run_id)
    return {"status": "deleted"}


@app.post("/api/generate")
def generate(request: GenerateRequest) -> dict:
    if not request.raw_content.strip():
        raise HTTPException(status_code=400, detail="Please provide an OpenAPI document or a plain-English description.")

    try:
        parsed_input = _parse_input(request)
        context = _build_generation_context(parsed_input, request)
        generated = generate_tests(context, request.framework)
        coverage = analyze_coverage(parsed_input, generated)
        gaps = suggest_missing_tests(parsed_input, generated)
        generated["coverage_gaps"] = gaps

        run_id = save_run(
            {
                "timestamp": None,
                "input_type": request.input_type,
                "framework": request.framework,
                "input_summary": request.raw_content[:500],
                "unit_tests": generated.get("unit", ""),
                "integration_tests": generated.get("integration", ""),
                "edge_cases": generated.get("edge_cases", ""),
                "coverage_pct": coverage.get("coverage_pct", 0),
            }
        )

        return {
            "run_id": run_id,
            "parsed_input": parsed_input,
            "generated_tests": generated,
            "coverage": coverage,
            "coverage_gaps": gaps,
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/api/export/github")
def export_github(request: GithubExportRequest) -> dict:
    if not request.repo.strip() or not request.token.strip():
        raise HTTPException(status_code=400, detail="Provide both a GitHub repo and token.")
    return push_to_github(token=request.token, repo=request.repo, tests=request.tests, framework=request.framework)


@app.post("/api/history/{run_id}/restore")
def restore_history(run_id: int) -> dict:
    run = get_run_by_id(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return {
        "run_id": run_id,
        "generated_tests": {
            "unit": run.get("unit_tests", ""),
            "integration": run.get("integration_tests", ""),
            "edge_cases": run.get("edge_cases", ""),
        },
        "coverage": {
            "total_endpoints": 0,
            "covered": 0,
            "uncovered": [],
            "coverage_pct": int(run.get("coverage_pct", 0) or 0),
        },
        "framework": run.get("framework", "pytest"),
        "input_type": run.get("input_type", "OpenAPI / Swagger"),
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend.api:app", host="0.0.0.0", port=8000, reload=True)
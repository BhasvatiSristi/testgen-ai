"""Streamlit entry point for the TestGen AI application."""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

# Make the repository root importable when Streamlit runs this file as a script.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.agent.context_builder import build_context
from backend.agent.coverage_analyzer import analyze_coverage
from backend.agent.coverage_gap_agent import suggest_missing_tests
from backend.agent.test_generator import generate_tests
from backend.parser.openapi_parser import parse_openapi
from backend.parser.plaintext_parser import parse_plaintext
from backend.storage.history_store import save_run
from frontend.components.config_panel import render_config_panel
from frontend.components.export_panel import render_export_panel
from frontend.components.input_panel import render_input_panel
from frontend.components.history_panel import render_history_panel
from frontend.components.output_panel import render_output_panel


st.set_page_config(page_title="TestGen AI", page_icon="🧪", layout="wide")
st.title("AI-Powered Test Case Generation Agent")
st.write("Generate unit, integration, and edge-case tests from API specs or plain-English requirements.")

if "generated_tests" not in st.session_state:
    st.session_state["generated_tests"] = {"unit": "", "integration": "", "edge_cases": ""}
if "coverage" not in st.session_state:
    st.session_state["coverage"] = {"total_endpoints": 0, "covered": 0, "uncovered": [], "coverage_pct": 0}
if "input_type" not in st.session_state:
    st.session_state["input_type"] = "OpenAPI / Swagger"
if "coverage_gaps" not in st.session_state:
    st.session_state["coverage_gaps"] = []
if "last_raw_content" not in st.session_state:
    st.session_state["last_raw_content"] = ""
if "last_input_type" not in st.session_state:
    st.session_state["last_input_type"] = "OpenAPI / Swagger"
if "auto_generate_gap" not in st.session_state:
    st.session_state["auto_generate_gap"] = False
if "pending_gap_scenario" not in st.session_state:
    st.session_state["pending_gap_scenario"] = None

with st.sidebar:
    config = render_config_panel()
    render_history_panel()

framework = config["framework"]
input_type, raw_content = render_input_panel()
focus_endpoint = st.session_state.get("focus_endpoint", "")
st.session_state["input_type"] = input_type
st.session_state["last_input_type"] = input_type

generated_tests = st.session_state["generated_tests"]
coverage = st.session_state["coverage"]
gap_suggestions = st.session_state.get("coverage_gaps", [])
pending_gap = st.session_state.get("pending_gap_scenario")

if focus_endpoint:
    st.info(f"Focused regeneration endpoint: {focus_endpoint}")

def _generate_tests_for_current_input(input_type_value: str, raw_content_value: str, framework_value: str, gap: dict | None = None):
    if input_type_value == "OpenAPI / Swagger":
        parsed_input = parse_openapi(raw_content_value)
    else:
        parsed_input = parse_plaintext(raw_content_value)

    context = build_context(parsed_input)
    if focus_endpoint:
        context = (
            f"{context}\n\n"
            f"Focus uncovered endpoint: {focus_endpoint}\n"
            "Generate additional tests that explicitly cover this endpoint."
        )
    if gap:
        context = (
            f"{context}\n\n"
            f"Missing scenario: {gap.get('missing_scenario', '')}\n"
            f"Target endpoint: {gap.get('endpoint', '')}\n"
            "Generate only this missing scenario and keep the response narrowly focused."
        )

    with st.spinner("Generating tests..."):
        generated = generate_tests(context, framework_value)

    coverage_data = analyze_coverage(parsed_input, generated)
    gaps = suggest_missing_tests(parsed_input, generated)
    generated["coverage_gaps"] = gaps

    st.session_state["generated_tests"] = generated
    st.session_state["coverage"] = coverage_data
    st.session_state["coverage_gaps"] = gaps
    st.session_state["last_raw_content"] = raw_content_value
    st.session_state["pending_gap_scenario"] = None
    st.session_state["auto_generate_gap"] = False

    save_run(
        {
            "timestamp": None,
            "input_type": input_type_value,
            "framework": framework_value,
            "input_summary": raw_content_value[:500],
            "unit_tests": generated.get("unit", ""),
            "integration_tests": generated.get("integration", ""),
            "edge_cases": generated.get("edge_cases", ""),
            "coverage_pct": coverage_data.get("coverage_pct", 0),
        }
    )

    return parsed_input


if st.session_state.get("auto_generate_gap") and st.session_state.get("last_raw_content", "").strip():
    _generate_tests_for_current_input(
        st.session_state.get("last_input_type", input_type),
        st.session_state["last_raw_content"],
        framework,
        st.session_state.get("pending_gap_scenario"),
    )

if st.button("Generate tests", type="primary"):
    if not raw_content.strip():
        st.error("Please provide an OpenAPI document or a plain-English description.")
        st.stop()

    st.session_state["last_input_type"] = input_type
    _generate_tests_for_current_input(input_type, raw_content, framework, None)

generated_tests = st.session_state["generated_tests"]
coverage = st.session_state["coverage"]
gap_suggestions = st.session_state.get("coverage_gaps", [])

if coverage.get("uncovered"):
    st.subheader("Uncovered endpoints")
    for uncovered_endpoint in coverage["uncovered"]:
        warning_col, button_col = st.columns([4, 1])
        with warning_col:
            st.warning(f"Uncovered endpoint: {uncovered_endpoint}")
        with button_col:
            button_key = f"generate_missing_{uncovered_endpoint.replace(' ', '_').replace('/', '_').replace('{', '_').replace('}', '_').lower()}"
            if st.button("Generate missing tests ↗", key=button_key):
                st.session_state["focus_endpoint"] = uncovered_endpoint
                st.session_state["pending_gap_scenario"] = {
                    "endpoint": uncovered_endpoint,
                    "missing_scenario": f"Generate focused tests for {uncovered_endpoint}",
                    "priority": "high",
                }
                st.session_state["auto_generate_gap"] = True
                st.rerun()

render_output_panel(
    generated_tests,
    coverage,
    framework,
    gap_suggestions=gap_suggestions,
)
st.divider()
render_export_panel(st.session_state["generated_tests"], framework)

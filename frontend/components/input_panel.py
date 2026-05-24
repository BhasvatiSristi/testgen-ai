"""Streamlit input panel for the TestGen AI app."""

from __future__ import annotations

from pathlib import Path

import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEMO_DIR = PROJECT_ROOT / "backend" / "demo_examples"
DEMO_FILES = {
    "Auth API": DEMO_DIR / "auth_api.yaml",
    "User CRUD": DEMO_DIR / "user_crud.yaml",
    "Payment flow": DEMO_DIR / "payment_flow.md",
}


def _read_uploaded_file(uploaded_file: object) -> str:
    if uploaded_file is None:
        return ""

    file_bytes = uploaded_file.getvalue()  # type: ignore[attr-defined]
    return file_bytes.decode("utf-8", errors="ignore").strip()


def _read_demo_example(demo_name: str) -> str:
    if demo_name == "— select demo —":
        return ""

    demo_path = DEMO_FILES.get(demo_name)
    if not demo_path or not demo_path.exists():
        return ""

    return demo_path.read_text(encoding="utf-8").strip()


def render_input_panel() -> tuple[str, str]:
    """Render the input controls and return the selected values."""

    input_type = st.selectbox(
        "Input type",
        ["OpenAPI / Swagger", "Plain English"],
        index=0,
    )
    demo_choice = st.selectbox(
        "Load demo",
        ["— select demo —", "Auth API", "User CRUD", "Payment flow"],
        index=0,
        key="demo_example_choice",
    )
    demo_content = _read_demo_example(demo_choice)
    uploaded_file = st.file_uploader(
        "Upload a .yaml, .json, or .py file",
        type=["yaml", "json", "py"],
    )
    uploaded_content = _read_uploaded_file(uploaded_file)
    source_content = uploaded_content or demo_content or st.session_state.get("raw_content_input", "")

    if uploaded_content:
        st.info("Using uploaded file")
    elif demo_content:
        st.info(f"Using demo: {demo_choice}")

    if source_content:
        st.session_state["raw_content_input"] = source_content

    raw_content = st.text_area(
        "Specification or requirement",
        height=280,
        placeholder="Paste an OpenAPI spec or describe the system in plain English.",
        key="raw_content_input",
    )
    if uploaded_content or demo_content:
        raw_content = source_content

    return input_type, raw_content

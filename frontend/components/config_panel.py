"""Streamlit configuration panel for TestGen AI."""

from __future__ import annotations

import streamlit as st


def render_config_panel() -> dict:
    """Render the advanced configuration controls."""

    st.subheader("Configuration")

    framework = st.selectbox(
        "Framework",
        ["pytest", "jest", "junit", "rspec"],
        index=0,
        key="config_framework",
    )
    test_types = st.multiselect(
        "Test types",
        ["Unit tests", "Integration tests", "Edge cases", "Mocks/Fixtures"],
        default=["Unit tests", "Integration tests", "Edge cases"],
        key="config_test_types",
    )
    coverage_depth_label = st.select_slider(
        "Coverage depth",
        options=["Basic", "Medium", "Deep"],
        value="Medium",
        key="config_coverage_depth",
    )

    depth_map = {"Basic": 1, "Medium": 2, "Deep": 3}
    test_limit_map = {"Basic": 5, "Medium": 10, "Deep": 15}
    st.caption(f"Depth target: {test_limit_map[coverage_depth_label]} tests max per category")

    return {
        "framework": framework,
        "test_types": test_types,
        "coverage_depth": depth_map[coverage_depth_label],
    }
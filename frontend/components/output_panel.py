"""Streamlit output panel for generated tests and coverage summary."""

from __future__ import annotations

import re

import streamlit as st


def _combined_test_count(generated_tests: dict) -> int:
    combined_text = "\n".join(
        value for value in (generated_tests or {}).values() if isinstance(value, str)
    )
    pattern = re.compile(r"^\s*(?:def\s+test_|it\s*\()", flags=re.MULTILINE)
    return len(pattern.findall(combined_text))


def _language_for_framework(framework: str) -> str:
    normalized = (framework or "").strip().lower()
    return {
        "pytest": "python",
        "jest": "javascript",
        "junit": "java",
        "rspec": "ruby",
    }.get(normalized, "text")


def _download_name(section: str) -> str:
    return {
        "unit": "unit_tests.py",
        "integration": "integration_tests.py",
        "edge_cases": "edge_case_tests.py",
    }[section]


def render_output_panel(generated_tests: dict, coverage: dict, framework: str, gap_suggestions: list[dict] | None = None):
    """Render the generated output, metrics, and download actions."""

    generated_tests = generated_tests or {}
    coverage = coverage or {}
    gap_suggestions = gap_suggestions or []
    language = _language_for_framework(framework)

    metric_col1, metric_col2, metric_col3 = st.columns(3)
    with metric_col1:
        st.metric("Tests generated", _combined_test_count(generated_tests))
    with metric_col2:
        st.metric("Endpoints covered", coverage.get("covered", 0))
    with metric_col3:
        st.metric("Coverage", f'{coverage.get("coverage_pct", 0)}%')

    tabs = st.tabs(["Unit tests", "Integration", "Edge cases", "Coverage gaps"])
    section_keys = ["unit", "integration", "edge_cases"]

    for tab, section in zip(tabs, section_keys):
        content = generated_tests.get(section, "")
        with tab:
            st.code(content, language=language)
            st.download_button(
                label=f"Download {section.replace('_', ' ').title()}",
                data=content,
                file_name=_download_name(section),
                mime="text/plain",
                use_container_width=True,
                key=f"download_{section}",
            )

    with tabs[3]:
        if not gap_suggestions:
            st.caption("No gap suggestions available yet.")
        else:
            for index, gap in enumerate(gap_suggestions):
                if not isinstance(gap, dict):
                    continue

                priority = str(gap.get("priority", "medium") or "medium").lower()
                endpoint = str(gap.get("endpoint", "") or "").strip()
                scenario = str(gap.get("missing_scenario", "") or "").strip()
                message = f"{endpoint} · {scenario}" if endpoint else scenario

                if priority == "high":
                    st.error(message)
                elif priority == "medium":
                    st.warning(message)
                else:
                    st.info(message)

                if st.button("Generate this test ↗", key=f"gap_generate_{index}"):
                    st.session_state["pending_gap_scenario"] = gap
                    st.session_state["auto_generate_gap"] = True
                    st.rerun()

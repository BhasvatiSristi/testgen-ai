"""Recent generation history panel."""

from __future__ import annotations

import streamlit as st

from backend.storage.history_store import get_all_runs, get_run_by_id


def render_history_panel():
    """Render recent runs and allow reloading a previous result."""

    st.subheader("Recent runs")
    runs = get_all_runs()

    if not runs:
        st.caption("No saved runs yet.")
        return

    for run in runs:
        title = f"{run['timestamp']} · {run['framework']} · {run['coverage_pct']}% coverage"
        with st.expander(title):
            st.caption(f"Input type: {run.get('input_type', '')}")
            st.caption(f"Summary: {run.get('input_summary', '')}")
            st.write("Unit tests")
            st.code(run.get("unit_tests", ""), language="text")
            st.write("Integration tests")
            st.code(run.get("integration_tests", ""), language="text")
            st.write("Edge cases")
            st.code(run.get("edge_cases", ""), language="text")

            if st.button("Reload this run", key=f"reload_run_{run['id']}"):
                full_run = get_run_by_id(int(run["id"]))
                st.session_state["generated_tests"] = {
                    "unit": full_run.get("unit_tests", ""),
                    "integration": full_run.get("integration_tests", ""),
                    "edge_cases": full_run.get("edge_cases", ""),
                }
                st.session_state["coverage"] = {
                    "total_endpoints": 0,
                    "covered": 0,
                    "uncovered": [],
                    "coverage_pct": int(full_run.get("coverage_pct", 0) or 0),
                }
                st.session_state["framework"] = full_run.get("framework", st.session_state.get("framework", "pytest"))
                st.session_state["input_type"] = full_run.get("input_type", st.session_state.get("input_type", "OpenAPI / Swagger"))
                st.rerun()
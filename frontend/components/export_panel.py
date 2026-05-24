"""Export and GitHub push panel for generated tests."""

from __future__ import annotations

import streamlit as st

from backend.integrations.github_pusher import push_to_github


FILE_NAMES = {
    "unit": "unit_tests.py",
    "integration": "integration_tests.py",
    "edge_cases": "edge_case_tests.py",
}


def _language_for_framework(framework: str) -> str:
    normalized = (framework or "").strip().lower()
    return {
        "pytest": "python",
        "jest": "javascript",
        "junit": "java",
        "rspec": "ruby",
    }.get(normalized, "text")


def render_export_panel(tests: dict, framework: str):
    """Render download and GitHub export controls."""

    tests = tests or {}
    code_language = _language_for_framework(framework)

    download_col1, download_col2, download_col3 = st.columns(3)
    with download_col1:
        st.download_button(
            "Download unit tests",
            data=tests.get("unit", ""),
            file_name=FILE_NAMES["unit"],
            mime="text/plain",
            key="export_download_unit",
            use_container_width=True,
        )
    with download_col2:
        st.download_button(
            "Download integration tests",
            data=tests.get("integration", ""),
            file_name=FILE_NAMES["integration"],
            mime="text/plain",
            key="export_download_integration",
            use_container_width=True,
        )
    with download_col3:
        st.download_button(
            "Download edge case tests",
            data=tests.get("edge_cases", ""),
            file_name=FILE_NAMES["edge_cases"],
            mime="text/plain",
            key="export_download_edge_cases",
            use_container_width=True,
        )

    repo = st.text_input("GitHub repo (owner/repo)", key="github_repo_input")
    token = st.text_input("GitHub token", type="password", key="github_token_input")

    github_col1, github_col2 = st.columns(2)
    with github_col1:
        if st.button("Push to GitHub", key="push_to_github_button", use_container_width=True):
            if not repo or not token:
                st.error("Provide both a GitHub repo and token.")
            else:
                result = push_to_github(token=token, repo=repo, tests=tests, framework=framework)
                if result.get("success"):
                    st.success("Pushed generated tests to GitHub.")
                    for url in result.get("urls", []):
                        st.write(url)
                else:
                    st.error(result.get("error") or "GitHub push failed.")

    with github_col2:
        if st.button("Copy all to clipboard", key="copy_all_tests_button", use_container_width=True):
            combined = "\n\n".join(
                [
                    "# Unit tests\n" + tests.get("unit", ""),
                    "# Integration tests\n" + tests.get("integration", ""),
                    "# Edge case tests\n" + tests.get("edge_cases", ""),
                ]
            )
            st.code(combined, language=code_language)
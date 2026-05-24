"""Configuration helpers for the TestGen AI backend."""

from __future__ import annotations

import os

from dotenv import load_dotenv

load_dotenv()

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "").strip()
MODEL = "mistral-large-latest"
MAX_TOKENS = 2048

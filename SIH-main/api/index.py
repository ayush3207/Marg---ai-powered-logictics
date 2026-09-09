"""
Vercel Serverless Function Entry Point
──────────────────────────────────────
This file wraps the existing FastAPI application so Vercel can run it
as a serverless function.  Vercel's @vercel/python runtime detects the
ASGI `app` object and serves it automatically.
"""

import os
import sys
from pathlib import Path

# ── Resolve paths ──────────────────────────────────────────────
# Vercel runs from the project root.  We need `backend/` on sys.path
# so that main.py's internal imports (e.g. `from services.xxx import …`)
# resolve correctly.
_PROJECT_ROOT = str(Path(__file__).resolve().parent.parent)
_BACKEND_DIR = os.path.join(_PROJECT_ROOT, "backend")

if _BACKEND_DIR not in sys.path:
    sys.path.insert(0, _BACKEND_DIR)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

# ── Import the FastAPI app ─────────────────────────────────────
# `main` resolves to backend/main.py because _BACKEND_DIR is first
# on sys.path.
from main import app  # noqa: E402

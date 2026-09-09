"""
Vercel Serverless Function Entry Point
──────────────────────────────────────
This file wraps the existing FastAPI application so Vercel can run it
as a serverless function.  Vercel looks for an `app` variable that is
an ASGI/WSGI-compatible application, or a `handler` function.

The mangum adapter converts ASGI (FastAPI) ↔ AWS Lambda / Vercel handler.
"""

import sys
from pathlib import Path

# ── Make the backend directory importable ──────────────────────
# Vercel runs this file from the project root, so we need to ensure
# that `backend/` is on sys.path so that `from services.xxx import …`
# works inside main.py exactly as it does locally.
_BACKEND_DIR = str(Path(__file__).resolve().parent.parent / "backend")
if _BACKEND_DIR not in sys.path:
    sys.path.insert(0, _BACKEND_DIR)

# ── Import the FastAPI app from the backend ────────────────────
from backend.main import app  # noqa: E402

# ── Vercel expects the variable to be named `app` ─────────────
# The import above already binds it.  Vercel's @vercel/python runtime
# automatically detects the ASGI `app` object and serves it.

"""
Vercel Serverless Function Entry Point
──────────────────────────────────────
Wraps the FastAPI app for Vercel's @vercel/python runtime.
"""

import os
import sys
import traceback
from pathlib import Path

# ── Resolve paths ──────────────────────────────────────────────
# When Vercel's root directory is set to SIH-main, this file lives at
# SIH-main/api/index.py.  __file__.parent.parent gives us SIH-main/.
_THIS_DIR = Path(__file__).resolve().parent          # .../api/
_PROJECT_ROOT = _THIS_DIR.parent                      # .../SIH-main/
_BACKEND_DIR = _PROJECT_ROOT / "backend"

# Add backend/ so that main.py's `from services.xxx import …` works
for p in [str(_BACKEND_DIR), str(_PROJECT_ROOT)]:
    if p not in sys.path:
        sys.path.insert(0, p)

# ── Import the FastAPI app ─────────────────────────────────────
try:
    from main import app  # backend/main.py
except Exception as e:
    # If the real app fails to import, create a minimal FastAPI app
    # that returns the actual error so we can debug on Vercel
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse

    app = FastAPI()

    _import_error = "".join(traceback.format_exception(type(e), e, e.__traceback__))

    @app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
    async def error_handler(path: str):
        return JSONResponse(
            status_code=500,
            content={
                "error": "Backend failed to start",
                "detail": str(e),
                "traceback": _import_error,
                "sys_path": sys.path,
                "backend_dir": str(_BACKEND_DIR),
                "backend_exists": _BACKEND_DIR.exists(),
                "backend_contents": (
                    [f.name for f in _BACKEND_DIR.iterdir()]
                    if _BACKEND_DIR.exists() else []
                ),
            },
        )

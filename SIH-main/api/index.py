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
# The repo structure is:
#   repo-root/
#     SIH-main/
#       api/index.py       ← THIS FILE
#       backend/main.py    ← FastAPI app
#
# __file__ → api/index.py  (relative to wherever Vercel's root is)
# We try both possible structures:
#   1. Root = SIH-main/ → backend/ is at ../backend relative to api/
#   2. Root = repo-root/ → backend/ is at ../SIH-main/backend

_THIS_DIR = Path(__file__).resolve().parent
_PARENT = _THIS_DIR.parent

# Try standard layout first (root = SIH-main/)
_BACKEND_DIR = _PARENT / "backend"
if not _BACKEND_DIR.exists():
    # Fallback: root = repo-root/, project is inside SIH-main/
    _BACKEND_DIR = _PARENT / "SIH-main" / "backend"

_BACKEND_STR = str(_BACKEND_DIR)
_PARENT_STR = str(_PARENT)

for p in [_BACKEND_STR, _PARENT_STR]:
    if p not in sys.path:
        sys.path.insert(0, p)

# ── Import the FastAPI app ─────────────────────────────────────
try:
    from main import app  # backend/main.py
except Exception as e:
    # Return the actual error as JSON for debugging
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse

    app = FastAPI()
    _err = "".join(traceback.format_exception(type(e), e, e.__traceback__))

    @app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
    async def error_handler(path: str):
        return JSONResponse(
            status_code=500,
            content={
                "error": "Backend failed to import",
                "detail": str(e),
                "traceback": _err,
                "cwd": os.getcwd(),
                "this_file": str(Path(__file__).resolve()),
                "backend_dir": _BACKEND_STR,
                "backend_exists": _BACKEND_DIR.exists(),
                "backend_contents": (
                    sorted(f.name for f in _BACKEND_DIR.iterdir())
                    if _BACKEND_DIR.exists() else []
                ),
                "sys_path": sys.path[:10],
            },
        )

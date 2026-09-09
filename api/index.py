"""
Vercel Serverless Function — Repo Root Fallback
────────────────────────────────────────────────
If Vercel's root directory is NOT set to SIH-main, this file
at repo-root/api/index.py handles the routing.
"""

import os
import sys
import traceback
from pathlib import Path

_THIS_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _THIS_DIR.parent
_BACKEND_DIR = _REPO_ROOT / "SIH-main" / "backend"

for p in [str(_BACKEND_DIR), str(_REPO_ROOT / "SIH-main")]:
    if p not in sys.path:
        sys.path.insert(0, p)

try:
    from main import app
except Exception as e:
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
                "backend_dir": str(_BACKEND_DIR),
                "backend_exists": _BACKEND_DIR.exists(),
            },
        )

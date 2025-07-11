from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from foe_foundry_data.powers import load_power_index, search_powers

from .logconfig import setup_logging
from .routes import monsters, powers

setup_logging()
log = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app):
    log.info("Initializing FastAPI app...")
    load_power_index()
    log.info("Running simple query to prime the index...")
    search_powers("Pack Tactics", limit=1)
    yield


app = FastAPI(lifespan=lifespan)

origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:3000",
    "http://localhost:3001",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1).*$",  # allow localhost* and 127.0.0.1*
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(powers.router)
app.include_router(monsters.router)

site_dir = Path(__file__).parent.parent / "site"

# Mounts the static site folder create by mkdocs
app.mount("/", StaticFiles(directory=site_dir, html=True), name="site")


# Middleware that sets Cache-Control headers for static file responses
@app.middleware("http")
async def cache_control_middleware(request: Request, call_next):
    response: Response = await call_next(request)

    # Only apply caching to successful static file responses
    if response.status_code == 200 and "/api" not in request.url.path:
        ext = Path(request.url.path).suffix.lower()

        if ext in [".webp", ".png", ".jpg", ".jpeg", ".gif", ".svg"]:
            response.headers["Cache-Control"] = "public, max-age=2592000"  # 30 days
        else:
            response.headers["Cache-Control"] = "public, max-age=86400"  # 1 day

    return response

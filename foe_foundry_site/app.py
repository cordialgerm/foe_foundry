from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from foe_foundry_search import setup_indexes

from .auth import routes as auth_routes
from .auth.dependencies import SESSION_SECRET
from .logconfig import setup_logging
from .routes import (
    catalog,
    geo,
    monster_templates,
    monsters,
    powers,
    pretty_monsters,
    redirects,
    search,
    statblocks,
    tags,
)

setup_logging()
log = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app):
    # load the power index at startup unless SKIP_INDEX_INIT is set
    if not os.environ.get("SKIP_INDEX_INIT"):
        setup_indexes()

    yield


app = FastAPI(lifespan=lifespan)

# Add session middleware for authentication
app.add_middleware(SessionMiddleware, secret_key=SESSION_SECRET, https_only=False)

origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:3000",
    "http://localhost:3001",
    "https://foe-foundry-stage.onrender.com",
    "https://foe-foundry.com",
    "https://www.foe-foundry.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1).*$",  # allow localhost* and 127.0.0.1*
    allow_methods=["*"],
    allow_headers=["*"],
)

site_dir = Path(__file__).parent.parent / "site"

# Store site_dir on app.state for access in route handlers
app.state.site_dir = site_dir

app.include_router(redirects.router)
app.include_router(auth_routes.router)
app.include_router(powers.router)
app.include_router(statblocks.router)
app.include_router(monsters.router)
app.include_router(monster_templates.router)
app.include_router(search.router)
app.include_router(catalog.router)
app.include_router(tags.router)
app.include_router(geo.router)
app.include_router(pretty_monsters.router)

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
